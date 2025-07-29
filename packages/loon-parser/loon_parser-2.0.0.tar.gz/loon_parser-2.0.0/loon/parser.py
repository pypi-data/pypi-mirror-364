import json
import re

def infer_value_type(value: str, labels=None, hidden_labels=None):
	value = value.strip()
	if value.startswith("[") and value.endswith("]"):
		return {"__ref__": value[1:-1].strip()}  # Defer resolution

	if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
		return value[1:-1]
	elif value.lower() == "true":
		return True
	elif value.lower() == "false":
		return False
	else:
		try:
			return float(value) if '.' in value else int(value)
		except ValueError:
			return value

def resolve_reference(value, labels, hidden_labels):
	ref = value[1:-1].strip() if value.startswith("[") else value.strip()
	all_labels = {**labels, **hidden_labels}

	if "." in ref:
		scope, identity = ref.split(".", 1)
		if ":" in scope:
			lbl, sp = scope.split(":", 1)
			data = all_labels[lbl][sp]
		else:
			data = all_labels[scope]
		return data.get(identity)
	elif ":" in ref:
		lbl, sp = ref.split(":", 1)
		return all_labels[lbl][sp]
	else:
		return all_labels[ref]

def resolve_lazy_refs(data, labels, hidden_labels):
	if isinstance(data, dict):
		for k, v in data.items():
			if isinstance(v, dict) and "__ref__" in v:
				data[k] = resolve_reference(f"[{v['__ref__']}]", labels, hidden_labels)
			else:
				resolve_lazy_refs(v, labels, hidden_labels)
	elif isinstance(data, list):
		for i in range(len(data)):
			if isinstance(data[i], dict) and "__ref__" in data[i]:
				data[i] = resolve_reference(f"[{data[i]['__ref__']}]", labels, hidden_labels)
			else:
				resolve_lazy_refs(data[i], labels, hidden_labels)

def parse_loon_file(filename, labels=None, spaces=None):
	if labels is None:
		labels = {}
	if spaces is None:
		spaces = {}

	hidden_labels = {}
	label_hidden_map = {}

	with open(filename, "r") as file:
		if not filename.endswith(".loon"):
			print("ERROR: file must be a .loon file")
			exit()
		code = [line.strip() for line in file if line.strip() and not line.strip().startswith("<")]

	current_label = None
	current_space = None
	label_stack = {}
	space_stack = {}
	insert_in_space = False

	for line in code:
		if (line.startswith("%(") or line.startswith("(")) and line.endswith(")"):
			is_hidden = line.startswith("%(")
			label_name = line[2:-1] if is_hidden else line[1:-1]
			current_label = label_name
			label_stack[current_label] = []
			label_hidden_map[current_label] = is_hidden
			current_space = None
			insert_in_space = False

		elif line.startswith(":"):
			current_space = line[1:]
			space_stack[current_space] = None
			insert_in_space = True

		elif line == "end:":
			result = space_stack[current_space]
			label_stack[current_label].append((current_space, result))
			spaces[current_space] = result
			insert_in_space = False
			current_space = None

		elif line == "end":
			result = {}
			for item in label_stack[current_label]:
				if isinstance(item, tuple):
					key, val = item
					result[key] = val
				elif isinstance(item, dict):
					result.update(item)
				elif isinstance(item, str):
					result[item] = None
			if label_hidden_map.get(current_label):
				hidden_labels[current_label] = result
			else:
				labels[current_label] = result
			current_label = None

		elif "=" in line:
			k, v = map(str.strip, line.split("=", 1))
			if k.startswith("$"):
				k = k[1:]
				all_labels = {**labels, **hidden_labels}

				if "." in k:
					scope, identity = k.split(".", 1)
					if ":" in scope:
						lbl, sp = scope.split(":", 1)
						if not (lbl in all_labels):
							print(f"ERROR: the label '{lbl}' was not found")
							exit()
						elif not (sp in all_labels[lbl]):
							print(f"ERROR: the space '{sp}' was not found")
							exit()
						else:
							k = identity
					else:
						if not (scope in all_labels):
							print(f"ERROR: the label '{scope}' was not found")
							exit()
						else:
							k = identity

			val = infer_value_type(v, labels, hidden_labels)
			if insert_in_space:
				blk = space_stack[current_space]
				if blk is None:
					blk = {}
					space_stack[current_space] = blk
				elif isinstance(blk, list):
					raise Exception(f"Cannot mix key-value with list in space '{current_space}'")
				blk[k] = val
			else:
				label_stack[current_label].append({k: val})

		elif line.startswith("@"):
			file_name = line[1:]
			if not file_name.endswith(".loon"):
				print("ERROR: file must be a .loon file")
				exit()
			temp_labels = {}
			parsed_import_file = parse_loon_file(file_name, temp_labels, spaces)
			if current_label is None:
				labels.update(parsed_import_file)
			else:
				if insert_in_space:
					blk = space_stack[current_space]
					if blk is None:
						blk = []
						space_stack[current_space] = blk
					elif isinstance(blk, list):
						raise Exception(f"Cannot mix key-value with list in space '{current_space}'")
					blk.append({current_label: parsed_import_file})
				else:
					label_stack[current_label].append(parsed_import_file)
			continue

		elif not line.startswith("->"):
			val = infer_value_type(line, labels, hidden_labels)
			if insert_in_space:
				blk = space_stack[current_space]
				if blk is None:
					blk = []
					space_stack[current_space] = blk
				elif isinstance(blk, dict):
					blk = [{k: v} for k, v in blk.items()]
					space_stack[current_space] = blk
				blk.append(val)
			else:
				label_stack[current_label].append(val)

		elif line.startswith("->"):
			raw = line[2:].strip()
			is_value_only = raw.endswith("&")
			if is_value_only:
				raw = raw[:-1].strip()

			all_labels = {**labels, **hidden_labels}

			if "." in raw:
				scope, identity = raw.split(".", 1)
				if ":" in scope:
					lbl, sp = scope.split(":", 1)
					data = all_labels[lbl][sp]
				else:
					data = all_labels[scope]
				val = data.get(identity)
				injected = val if is_value_only else {identity: val}

			elif ":" in raw:
				lbl, sp = raw.split(":", 1)
				data = all_labels[lbl][sp]
				injected = data if is_value_only else {sp: data}

			else:
				data = all_labels[raw]
				injected = data if is_value_only else {raw: data}

			if insert_in_space:
				blk = space_stack[current_space]
				if is_value_only:
					if blk is None:
						blk = []
						space_stack[current_space] = blk
					elif isinstance(blk, dict):
						blk = [{k: v} for k, v in blk.items()]
						space_stack[current_space] = blk
					blk.append(injected)
				else:
					if blk is None:
						blk = {}
						space_stack[current_space] = blk
					elif isinstance(blk, list):
						raise Exception(f"Cannot mix structured injection with list in space '{current_space}'")
					blk.update(injected)
			else:
				label_stack[current_label].append(injected)

	for label in labels.values():
		resolve_lazy_refs(label, labels, hidden_labels)

	return labels
