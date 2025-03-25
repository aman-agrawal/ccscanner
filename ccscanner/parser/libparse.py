import re

def expand_variable(value, variables, visited=None):
    """Recursively expands variables in a value list."""
    if visited is None:
        visited = set()

    expanded_values = []
    for item in value:
        if item.startswith("$(") and item.endswith(")"):
            var_name = item[2:-1]  # Extract variable name
            if var_name in variables and var_name not in visited:
                visited.add(var_name)
                expanded_values.extend(expand_variable(variables[var_name]["value"], variables, visited))
            else:
                expanded_values.append(item)
        else:
            expanded_values.append(item)

    return expanded_values

def extract_libraries(variables, targets):
    normalized_variables = {k: v for k, v in variables.items()}  # Preserve original keys

    # Expand variables to resolve all library-related values
    lib_vars = {}
    for var_name, var_data in normalized_variables.items():
        expanded_values = expand_variable(var_data.get("value", []), normalized_variables)
        if any(v.startswith("-l") for v in expanded_values):
            lib_vars[var_name] = expanded_values
            # print("var_name:" + var_name + ":" + str(expanded_values))

    # Extract libraries from LIBS-like variables
    linked_libs = []
    for var_values in lib_vars.values():
        linked_libs.extend([lib for lib in var_values if lib.startswith("-l")])

    # Identify targets using LIBS (expanded)
    used_in_targets = []
    for target, data in targets.items():
        for stmt in data.get("statements", []):
            expanded_stmt = " ".join(expand_variable(stmt.split(), normalized_variables))
            if any(lib in expanded_stmt for lib in linked_libs):  # Check expanded form
                used_in_targets.append(target)
                break

    # Detect direct library usage
    direct_library_usage = {}
    lib_pattern = re.compile(r"(-l\w+)")
    for target, data in targets.items():
        for stmt in data.get("statements", []):
            expanded_stmt = " ".join(expand_variable(stmt.split(), normalized_variables))
            direct_libs = lib_pattern.findall(expanded_stmt)
            if direct_libs:
                if target not in direct_library_usage:
                    direct_library_usage[target] = []
                direct_library_usage[target].extend(direct_libs)

    return {
        "libraries": list(set(linked_libs)),
        "used_in_targets": used_in_targets,
        "direct_library_usage": direct_library_usage
    }

# Example input
# variables = {
#     'CXX': {'operator': '?=', 'value': ['g++']},
#     'lib_base': {'operator': '=', 'value': ['-lssl', '-lcrypto']},
#     'LIB_EXTRA': {'operator': '=', 'value': ['-lz']},
#     'LD_Dependencies': {'operator': '=', 'value': ['-lb']},
#     'LIB_RECURSIVE': {'operator': '=', 'value': ['$(LD_Dependencies)', '-la']},
#     'LIBS': {'operator': '=', 'value': ['$(lib_base)', '$(LIB_EXTRA)', '$(LIB_RECURSIVE)']},
#     'CUSTOM_LIBS': {'operator': '=', 'value': ['$(LIBS)', '-lpthread']},  # Indirect reference
#     'LibPath': {'operator': '=', 'value': ['-L/usr/lib']}
# }
# targets = {
#     '.PHONY': {'dependencies': ['all'], 'statements': []},
#     '$(BIN_PATH)/$(BIN_NAME)': {'dependencies': ['$(OBJECTS)'], 'statements': [
#         '\t$(CXX) $(OBJECTS) -o $@ $(CUSTOM_LIBS)',  # Indirect library reference
#         '\t$(CXX) $(OBJECTS) -o $@ -lm -lcustomlib'
#     ]}
# }

# result = extract_libraries(variables, targets)
# print(result)
