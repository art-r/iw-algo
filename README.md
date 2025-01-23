# IW Algo

This repo holds the source code for the IntroWeek Workshop that sorts and assigns students to groups


## Config file description
The config file needs to contain this:

| Key | Description |
|---|---|
| nameK | the name of the column holding the student name |
| sidK | the name of the column holding the student number |
| prefMainK | the base name of the column(s) holding the preference |
| buddyK | the name of the column holding the buddy group |
| catK | the name of the column holding the workshp preferences |
| categories | **Dict** containing all available categories as keys and their limit and the info whether it is special as value |


Notes about the config file:
- prefMainK:\
This is the base name of the pref column and will then be prefixed w a number according to amountC. E.g., prefMainK="preference", amountC=2 will give the two columns "preference1" and "preference2".

- categories:\
This is a dictionary holding as keys the available category names and as value their limit (-1 meaning unlimited), the info whether it is a special category that needs to mix people so that the least amount are from the same buddy group, and the amount of sub-groups (only applicable for special categories!). E.g., `{"Vikings":[25,true,3], "Backup":[-1,false,0]}` means that category `Backup` has no limit, and that category `Vikings` has a limit of 25 people and is a special category, meaning that there will be 3 sub-groups where people need to be distributed among so that the least amount are from the same buddy group.

## Running logic
- The algorithm will assign students to a workshop based upon a first-come-first-server basis
- If a workshop's capacity is reached then it will try to do the same for the 2nd, 3rd, ... preference
- If all workshops are full and a student wasnt able to get a place then it will assign them to "UNASSIGNABLE"
- After this the algorithm will distribute students in the respective categories to subgroups
- It will do so by trying to maximize the diversity in the subgroups based upon the buddygroup number of the student

- Assigning remaining students is done under the consideration of the workshop limits

## Important caveats:
- The algorithm does not guarantee that there are exactly X amount of students per subgroup (if for example there are supposed to be 5 groups and the overall capacity of the workshop is 50 this implies 10 students per group, BUT if less students select this workshop than required then there will be subgroups with less than 10 students!)
- Assigning remaining students (i.e. students that did not submit a preference) considers the workshop limits but DOES NOT consider the subgroup limits, so this assignment may result in a subgroup having more than the desired amount of students!

## Explanation of the files in this repository:

| File | Explanation |
|---|---|
| `libraries/iw_handler.py` | The core assignment file |
| `script_wrapper.py` | Wrapper that runs the core assignment algorithm from the commandline |
| `app.py` | Alternative wrapper for the core assignment algorithm which runs in the browser using streamlit |
| `assign_remaining.py` | File that assign remaining students |
| `verifier.py` | Script that prints some statistics about the created groups to spot mistakes |
| `extract_buddy_groups.py` | File that creates files per buddy group (easier for distribution) |

## Running flow (local only):
1. Run script_wrapper.py
2. Run assign_remaining.py
3. Run verifier.py
4. Run extract_buddy_groups.py
