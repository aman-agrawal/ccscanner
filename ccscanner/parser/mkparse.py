"""
Makefile Parser
"""
import os

class Parser():
    """
    Makefile - make build system configuration file - parser
    """
    def __init__(self, makefile_name="Makefile", makefile_path="."):
        """
        Class Constructor
        """
        self.makefile_name = makefile_name
        self.makefile_path = makefile_path

    def ast_parse(self, makefile_string_contents=None):
        """
        Makefile parser core unit

        :: Params
        - makefile_string_contents : Specify the Makefile content body (after splitting by newline) you wish to import and parse into the memory buffer
            + Type: String|List
            + Default: ""

        :: Output
        - targets: Contains the targets/instructions/rules and the attached dependencies and statements
            + Type: Dictionary
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables : Contains the variables and the attached operator (delimiter) and value
            + Type: Dictionary 
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List
        - comments : Pass the updated global comments list you wish to export (NOTE: Currently unused; for future development plans)
            + Type: Dictionary 
            - Format
                {
                    "line-number" : comment-from-that-line
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - line-number: The line number; this is mapped to the comment stored at that line
        """
        # Initialize Variables
        targets = {}
        variables = {}
        curr_target = None
        curr_target_name = ""
        line_number = 0
        comments = {} # Store comments here; map line number to the comment
        operator_checklist = ["=", ":=", "?="]

        # Process and perform data validation + sanitization
        ## Null-value data validation
        if makefile_string_contents != None:
            ## Check if content type is string: Split it by newline into a list
            if type(makefile_string_contents) == str:
                # String is provided
                # Split makefile_string into a list
                makefile_string_contents = makefile_string_contents.split("\n")

            # Iterate through Makefile list and import 
            for line in makefile_string_contents:
                # Remove comments
                # line = line.split('#', 1)[0]
                line = line.rstrip()

                # Check if line is empty after removing comments
                if not line:
                    # Line is empty, continue
                    continue

                # Check if line contains a '#' (a comment)
                if line[0] == '#':
                    # Store all comments
                    comments[line_number] = line

                # Check if line contains a '=' (defines a variable)
                elif '=' in line:
                    # Check if line contains spaces
                    has_space = False
                    for char in line:
                        if char == ' ':
                            has_space = True
                            break

                    # Line contains space
                    if has_space:
                        # Initialize Variables
                        operator_idx = -1
                        operator = "="

                        # Split the '=' to a LHS and RHS
                        parts = line.split(' ')

                        # Validate/Verify parts list is more than or equals to 2 : Name, Operator and Value, value might be empty
                        if len(parts) >= 2:
                            # Initialize Variables
                            variable_value = []

                            # Strip the newline off the first element which is the variable name
                            variable_name = parts[0].strip()

                            # Check variable name for special characters (=, :=, ?=)
                            for tmp in operator_checklist:
                                # Obtain position index
                                tmp_pos_idx = variable_name.find(tmp)
                                if tmp_pos_idx > -1:
                                    operator_idx = tmp_pos_idx
                                    operator = tmp

                            # Obtain Operator
                            if operator_idx > -1:
                                # Split parts according to the newly-discovered operator
                                parts = line.split(operator)

                                # variable_name = variable_name[:operator_idx]
                                variable_name = parts[0].strip()

                                # Check if variable value is provided
                                if len(parts) >= 2:
                                    # Obtain variable value by splitting the string into a list
                                    variable_value = parts[1].split(' ')
                            else:
                                operator = parts[1]

                                # Check if variable value is provided
                                if len(parts) >= 3:
                                    # Obtain variable value
                                    variable_value = parts[2:]

                            # Map the variable value to the variable name in the entry mapping
                            variables[variable_name] = {'operator': operator, 'value': variable_value}
                    else:
                        # Line does not contain spaces, carry over

                        # Initialize Variables
                        variable_value = []
                        operator_idx = -1
                        operator = "="

                        # Check variable name for special characters (=, :=, ?=)
                        for tmp in operator_checklist:
                            # Obtain position index
                            tmp_pos_idx = line.find(tmp)
                            if tmp_pos_idx > -1:
                                operator_idx = tmp_pos_idx
                                operator = tmp

                        # Split the first occurence delimiter to a LHS and RHS
                        parts = line.split(operator, 1)

                        # Validate/Verify parts list is more than or equals to 2 : Name, Operator and Value, value might be empty
                        # Strip the newline off the first element which is the variable name
                        variable_name = parts[0].strip()

                        # Obtain variable value
                        variable_value = parts[1:]

                        # Map the variable value to the variable name in the entry mapping
                        variables[variable_name] = {'operator': operator, 'value': variable_value}

                # Check if line contains ':' (defines a target)
                elif ':' in line:
                    # Check if line ends with ':' (does not have any dependencies)
                    if line.endswith(':'):
                        # Ends with ':' == there are no dependencies, also is definitely a target
                        curr_target_name = line.split(':')[0].strip()

                        # Initialize a new entry for the current target
                        targets[curr_target_name] = {"dependencies" : [], "statements" : []}
                    else:
                        # Does not end with ':' == there are dependencies

                        # Check if line is really a target and not a statement
                        if not ('\t' in line):
                            # This is a target with dependencies

                            # Split line by ':'
                            curr_target = line.split(':')
                            curr_target_name = curr_target[0].strip()
                            curr_target_dependencies = curr_target[1].strip()

                            # Initialize a new entry for the current target
                            targets[curr_target_name] = {"dependencies" : [], "statements" : []}

                            # Null-value validation
                            if curr_target_dependencies == "":
                                curr_target_dependencies = None

                            # Remove newline
                            # current_target = line[:-1].rstrip()

                            # Check if dependencies are required
                            if not(curr_target_dependencies == None):
                                # Are required
                                # Append dependencies to the current target
                                targets[curr_target_name]['dependencies'].append(curr_target_dependencies)

                # Not target = statements, append statements to the target

                # Check for empty name
                if not (curr_target_name == '') :
                    # There's tab, a target does not have indentations (means that this is a statement)

                    # Store each row of the target's recipe in its own list
                    targets[curr_target_name]['statements'].append(line.rstrip())

                # Increment Line Number
                line_number += 1

            for curr_target_name,curr_target_values in targets.items():
                # Get current target's dependencies
                curr_target_dependencies = curr_target_values["dependencies"]

                # Get current target's statements
                curr_target_statements = curr_target_values["statements"]

                # Remove the first line from the list
                targets[curr_target_name]['statements'] = curr_target_statements[1:]

        return [targets, variables, comments]

    def parse_makefile(self, makefile_name="Makefile", makefile_path=".") -> list:
        """
        Parse Makefile into Python dictionary (Key-Value/HashMap) object

        :: Syntaxes
        :: =======
        :: Makefile variables Format:
            [variable-name] = [values ...]
     
        :: Makefile target/rules Format:
             [target-name]: [dependencies]
                 # statements...

        :: Output
        - targets: Pass the new targets list you wish to export
            + Type: Dictionary
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables : Pass the new variables list you wish to export
            + Type: Dictionary 
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List
        - comments : Pass the updated global comments list you wish to export (NOTE: Currently unused; for future development plans)
            + Type: Dictionary 
            - Format
                {
                    "line-number" : comment-from-that-line
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - line-number: The line number; this is mapped to the comment stored at that line
        """
        # Initialize Variables
        targets = {}
        variables = {}
        curr_target = None
        curr_target_name = ""
        line_number = 0
        comments = {} # Store comments here; map line number to the comment
        operator_checklist = ["=", ":=", "?="]

        # Process and perform data validation + sanitization

        ## Use the default Makefile file name if not provided
        if makefile_name == "":
            makefile_name = self.makefile_name

        ## Use the default Makefile file path if not provided
        if makefile_path == "":
            makefile_path = self.makefile_path

        # Try to open the Makefile
        try:
            with open(os.path.join(makefile_path, makefile_name), 'r') as makefile:
                for line in makefile:
                    # Remove comments
                    # line = line.split('#', 1)[0]
                    line = line.rstrip()

                    # Check if line is empty after removing comments
                    if not line:
                        # Line is empty, continue
                        continue

                    # Check if line contains a '#' (a comment)
                    if line[0] == '#':
                        # Store all comments
                        comments[line_number] = line

                    # Check if line contains a '=' (defines a variable)
                    elif '=' in line:
                        # Check if line contains spaces
                        has_space = False
                        for char in line:
                            if char == ' ':
                                has_space = True
                                break

                        # Line contains space
                        if has_space:
                            # Initialize Variables
                            operator_idx = -1
                            operator = "="

                            # Split the '=' to a LHS and RHS
                            parts = line.split(' ')

                            # Validate/Verify parts list is more than or equals to 2 : Name, Operator and Value, value might be empty
                            if len(parts) >= 2:
                                # Initialize Variables
                                variable_value = []

                                # Strip the newline off the first element which is the variable name
                                variable_name = parts[0].strip()

                                # Check variable name for special characters (=, :=, ?=)
                                for tmp in operator_checklist:
                                    # Obtain position index
                                    tmp_pos_idx = variable_name.find(tmp)
                                    if tmp_pos_idx > -1:
                                        operator_idx = tmp_pos_idx
                                        operator = tmp

                                # Obtain Operator
                                if operator_idx > -1:
                                    # Split parts according to the newly-discovered operator
                                    parts = line.split(operator)

                                    # variable_name = variable_name[:operator_idx]
                                    variable_name = parts[0].strip()

                                    # Check if variable value is provided
                                    if len(parts) >= 2:
                                        # Obtain variable value by splitting the string into a list
                                        variable_value = parts[1].split(' ')
                                else:
                                    operator = parts[1]

                                    # Check if variable value is provided
                                    if len(parts) >= 3:
                                        # Obtain variable value
                                        variable_value = parts[2:]

                                # Map the variable value to the variable name in the entry mapping
                                variables[variable_name] = {'operator': operator, 'value': variable_value}
                        else:
                            # Line does not contain spaces, carry over

                            # Initialize Variables
                            variable_value = []
                            operator_idx = -1
                            operator = "="

                            # Check variable name for special characters (=, :=, ?=)
                            for tmp in operator_checklist:
                                # Obtain position index
                                tmp_pos_idx = line.find(tmp)
                                if tmp_pos_idx > -1:
                                    operator_idx = tmp_pos_idx
                                    operator = tmp

                            # Split the first occurence delimiter to a LHS and RHS
                            parts = line.split(operator, 1)

                            # Validate/Verify parts list is more than or equals to 2 : Name, Operator and Value, value might be empty
                            # Strip the newline off the first element which is the variable name
                            variable_name = parts[0].strip()

                            # Obtain variable value
                            variable_value = parts[1:]

                            # Map the variable value to the variable name in the entry mapping
                            variables[variable_name] = {'operator': operator, 'value': variable_value}

                    # Check if line contains ':' (defines a target)
                    elif ':' in line:
                        # Check if line ends with ':' (does not have any dependencies)
                        if line.endswith(':'):
                            # Ends with ':' == there are no dependencies, also is definitely a target
                            curr_target_name = line.split(':')[0].strip()

                            # Initialize a new entry for the current target
                            targets[curr_target_name] = {"dependencies" : [], "statements" : []}
                        else:
                            # Does not end with ':' == there are dependencies

                            # Check if line is really a target and not a statement
                            if not ('\t' in line):
                                # This is a target with dependencies

                                # Split line by ':'
                                curr_target = line.split(':')
                                curr_target_name = curr_target[0].strip()
                                curr_target_dependencies = curr_target[1].strip()

                                # Initialize a new entry for the current target
                                targets[curr_target_name] = {"dependencies" : [], "statements" : []}

                                # Null-value validation
                                if curr_target_dependencies == "":
                                    curr_target_dependencies = None

                                # Remove newline
                                # current_target = line[:-1].rstrip()

                                # Check if dependencies are required
                                if not(curr_target_dependencies == None):
                                    # Are required
                                    # Append dependencies to the current target
                                    targets[curr_target_name]['dependencies'].append(curr_target_dependencies)

                    # Not target = statements, append statements to the target

                    # Check for empty name
                    if not (curr_target_name == '') :
                        # There's tab, a target does not have indentations (means that this is a statement)

                        # Store each row of the target's recipe in its own list
                        targets[curr_target_name]['statements'].append(line.rstrip())

                    # Increment Line Number
                    line_number += 1

                for curr_target_name,curr_target_values in targets.items():
                    # Get current target's dependencies
                    curr_target_dependencies = curr_target_values["dependencies"]

                    # Get current target's statements
                    curr_target_statements = curr_target_values["statements"]

                    # Remove the first line from the list
                    targets[curr_target_name]['statements'] = curr_target_statements[1:]

                # Close file after usage
                makefile.close()
        except FileNotFoundError:
            print("Makefile not found.")

        return [targets, variables, comments]

    def parse_makefile_string(self, makefile_string="") -> list:
        """
        Parse a Makefile syntax string into Python dictionary (Key-Value/HashMap) object

        :: Params
        - makefile_string : Specify the Makefile content body you wish to import and parse into the memory buffer
            + Type: String
            + Default: ""

        :: Syntaxes
        :: =======
        - Makefile variables Format:
            ```
            [variable-name] = [values ...]
            ```
     
        - Makefile target/rules Format:
            ```
            [target-name]: [dependencies]
                # statements...
            ```

        :: Output
        - targets: Pass the new targets list you wish to export
            + Type: Dictionary
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables : Pass the new variables list you wish to export
            + Type: Dictionary 
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List
        - comments : Pass the updated global comments list you wish to export (NOTE: Currently unused; for future development plans)
            + Type: Dictionary 
            - Format
                {
                    "line-number" : comment-from-that-line
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - line-number: The line number; this is mapped to the comment stored at that line
        """
        # Initialize Variables
        targets = {}
        variables = {}
        comments = {} # Store comments here; map line number to the comment

        # Process and perform data validation + sanitization
        if makefile_string != "":
            # String is provided
            # Split makefile_string into a list
            makefile_string_contents = makefile_string.split("\n")

            targets, variables, comments = self.ast_parse(makefile_string_contents)

        return [targets, variables, comments]

    def export_Makefile(self, targets:dict, variables:dict, makefile_name="Makefile", makefile_path=".") -> str:
        """
        Export the targets and variables list into an output Makefile

        :: Params
        - targets: Pass the new targets list you wish to export
            + Type: Dictionary
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables : Pass the new variables list you wish to export
            + Type: Dictionary 
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List
        - makefile_name : Specify the name of the output Makefile to export to
            + Type: String
            + Default Value: "Makefile"
        - makefile_path : Specify the path containing the output Makefile to export to
            + Type: String
            + Default Value: "."

        :: Output
        - File Name: [makefile_path]/[makefile_name]
        - File Type: Makefile
        - Format:
            ```
            [variable-name] = variable values
            [target-name] : your dependencies here
                # Instructions/statements
            ```
        """
        # Initialize Variables
        error_msg = ""
        makefile_fullpath = os.path.join(makefile_path, makefile_name)

        # Check if file exists
        if not (os.path.isfile(makefile_fullpath)):
            # Open file
            with open(makefile_fullpath, "a+") as export_Makefile:
                # Loop through all variables
                for variable_name, variable_mappings in variables.items():
                    # Obtain variable map operator
                    variable_operator = variable_mappings["operator"]

                    # Obtain variable values
                    variable_values = ' '.join(variable_mappings["value"])

                    # Write to Makefile
                    out_str = "{} {} {}\n".format(variable_name, variable_operator, variable_values)
                    export_Makefile.write(out_str)

                export_Makefile.write("\n")

                # Loop through all targets
                for target_name, target_mappings in targets.items():
                    # Obtain target dependencies
                    target_dependencies = ' '.join(target_mappings["dependencies"])

                    # Obtain target statements
                    target_statements = '\n'.join(target_mappings["statements"])

                    # Write to Makefile
                    out_str = "{}: {}\n{}\n".format(target_name, target_dependencies, target_statements)
                    export_Makefile.write(out_str + "\n")

                # Close file after usage
                export_Makefile.close()
        else:
            error_msg = "Makefile {} already exists".format(makefile_fullpath)

        return error_msg

    def format_makefile_Contents(self, targets=None, variables=None) -> dict:
        """
        Format provided makefile targets and variables into content strings

        :: Params
        - targets: Specify the Makefile targets to format
            + Type: Dictionary
            + Default: None
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables: Specify the Makefile variables to format
            + Type: Dictionary
            + Default: None
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List

        :: Output
        - contents: Dictionary (key-value) Mapping of the formatted strings, stored in a list of the targets and variables respectively
            + Type: Dictionary
            - Key-Value mappings
                - targets : List of all targets formatted into a printable string
                    + Type: List
                - variables : List of all variables formatted into a printable string
                    + Type: List
        """
        # Initialize Variables
        contents = {"targets" : [], "variables" : []}

        # Check if variables is empty
        if variables != None:
            for var_name, var_values in variables.items():
                # Get variable operator
                curr_var_operator = var_values["operator"]

                # Get variable value
                curr_var_value = ' '.join(var_values["value"])

                # Format current variable
                curr_out_string = "{} {} {}".format(var_name, curr_var_operator, curr_var_value)
                contents["variables"].append(curr_out_string)

        # Check if targets is empty
        if targets != None:
            for target_name, target_settings in targets.items():
                # Get current target dependencies
                curr_target_dependencies = ' '.join(target_settings["dependencies"])

                # Get current target statements
                curr_target_statements = '\n'.join(target_settings["statements"])

                # Format current variable
                curr_out_string = "{}: {}\n{}\n".format(target_name, curr_target_dependencies, curr_target_statements)
                contents["targets"].append(curr_out_string)

        return contents

    def trim_contents(self, targets=None, variables=None) -> list:
        """
        Trim and remove all special characters ("\n", "\t" etc) from the imported file contents

        :: Params
        - targets: Pass the new targets list you wish to export
            + Type: Dictionary
            - Format
                {
                    "target-name" : {
                        "dependencies" : [your, dependencies, here],
                        "statements" : [your, statements, here]
                    }
                }
            - Key-Value Explanation
                - target-name : Each entry of 'target-name' contains a Makefile build target/instruction/rule 
                    - Key-Value Mappings
                        - dependencies : Specify a list of all dependencies 
                            - Notes: 
                                - Dependencies are the pre-requisite rules to execute before executing the mapped target
                                    - i.e.
                                        [target-name]: [dependencies ...]
                        - statements : Specify a list of all rows of statements to write under the target
        - variables : Pass the new variables list you wish to export
            + Type: Dictionary 
            - Format
                {
                    "variable-name" : {
                        "operator" : "operator (i.e. =|?=|:=)",
                        "value" : [your, values, here]
                    }
                }
            - Key-Value Explanation
                - variable-name : Each entry of 'variable-name' contains a Makefile variable/ingredient
                    - Key-Value Mappings
                        - operator : Specify the operator to map the variable to its value string/array/list
                            + Type: String
                            - Operator Keyword Types
                                + '='
                                + '?='
                                + ':='
                        - value : Specify the value string/array/list (as a list) that you want to map to the variable
                            + Type: List
        """
        # Initialize Variables

        # Check if target is provided
        if targets != None:
            # Strip all special characters from targets and variables
            for target_name, target_mappings in targets.items():
                # Get target dependencies and statements
                curr_target_dependencies:list = target_mappings["dependencies"]
                curr_target_statements:list = target_mappings["statements"]

                # Loop through dependencies list
                for i in range(len(curr_target_dependencies)):
                    # Get current dependency
                    curr_dependency = curr_target_dependencies[i]

                    # Strip the current dependency
                    curr_dependency_stripped = curr_dependency.strip()

                    # Replace values with stripped dependencies
                    targets[target_name]["dependencies"][i] = curr_dependency_stripped

                # Loop through statements list
                for i in range(len(curr_target_statements)):
                    # Get current dependency
                    curr_statement = curr_target_statements[i]

                    # Strip the current statement
                    curr_statement_stripped = curr_statement.strip()

                    # Replace values with stripped statements
                    targets[target_name]["statements"][i] = curr_statement_stripped

        # Check if variables is provided
        if variables != None:
            # Strip all special characters from targets and variables
            for variable_name, variable_mappings in variables.items():
                # Get variable key-values
                curr_variable_values:list = variable_mappings["value"]

                # Loop through variable values list
                for i in range(len(curr_variable_values)):
                    # Get current value
                    curr_value = curr_variable_values[i]

                    # Strip the current dependency
                    curr_value_stripped = curr_value.strip()

                    # Replace values with stripped values
                    variables[variable_name]["value"][i] = curr_value_stripped

        # Check if results is found
        if (targets != None) and (variables != None):
            return [targets, variables]
        elif (targets != None):
            return targets
        elif (variables != None):
            return variables
        else:
            return []

