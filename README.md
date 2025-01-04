# IW Algo

This repo holds the source code for the IntroWeek Algorithm that sorts and assigns students to groups

The config file needs to contain this:

| Key | Description |
|---|---|
| nameK | the name of the column holding the student name |
| sidK | the name of the column holding the student number |
| prefMainK | the base name of the column(s) holding the preference |
| categories | **Dict** containing all available categories as keys and their limit and the info whether it is special as value |
| extsidK | the name of the column in the extra file holding the student number |
| extBK | the name of the column in the extra file holding buddy group number |


Notes about the config file:
- prefMainK:\
This is the base name of the pref column and will then be prefixed w a number according to amountC. E.g., prefMainK="preference", amountC=2 will give the two columns "preference1" and "preference2".

- categories:\
This is a dictionary holding as keys the available category names and as value their limit (-1 meaning unlimited), the info whether it is a special category that needs to mix people so that the least amount are from the same buddy group, and the amount of sub-groups (only applicable for special categories!). E.g., `{"Vikings":[25,true,3], "Backup":[-1,false,0]}` means that category `Backup` has no limit, and that category `Vikings` has a limit of 25 people and is a special category, meaning that there will be 3 sub-groups where people need to be distributed among so that the least amount are from the same buddy group.