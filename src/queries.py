# Get authenticated
# per session
"/authenticate?key=a3yr2ryr0rerygw98ryu0.." # uuid


# List directory
"/list?path=&recursive=false&itemtype=all"  # list all in root

"/list?path=&recursive=true&itemtype=all"  # list all in root recursively
"/list?path=&recursive=false&itemtype=file"  # list all files in root
"/list?path=&recursive=true&itemtype=file"  # list all files in root recursively
"/list?path=&recursive=false&itemtype=folder"  # list all directories in root
"/list?path=&recursive=true&itemtype=folder"  # list all directories in root recursively

"/list?path=src&recursive=false&itemtype=all"  # list all in root/src
"/list?path=src&recursive=true&itemtype=all"  # list all in root/src recursively
"/list?path=src&recursive=false&itemtype=file"  # list all files in root/src
"/list?path=src&recursive=true&itemtype=file"  # list all files in root/src recursively
"/list?path=src&recursive=false&itemtype=folder"  # list all directories in root/src
"/list?path=src&recursive=true&itemtype=folder"  # list all directories in root/src recursively

# File content
"/content?path=src/dash.ts&lines=3-3"  # line 3
"/content?path=src/dash.ts&lines=1-*"  # all lines
"/content?path=src/dash.ts&lines=3-*"  # all lines from line 3
"/content?path=src/dash.ts&lines=1-23"  # line 1 to line 23 # if only 20 lines avaible 23 is taken as 20
"/content?path=src/dash.ts&lines=*-20"  # all lines upto line 20

# -----------------------

# Create folder or file
"/create?path=src/components&itemtype=folder"
"/create?path=src/dash.ts&itemtype=file"

# -----------------------

# Rename folder or file
"/rename?path=src/components&newname=ui&itemtype=folder"
"/rename?path=src/pages/dash.tsx&newname=dashboard.tsx&itemtype=file"

# -----------------------

# Copy folder or file
"/copy?src=src/components&dest=src/ui&itemtype=folder"  # new folder will be src/ui/components
"/copy?src=src/pages/dash.tsx&dest=src/ui&itemtype=file"  # new file will be src/ui/dash.tsx

# -----------------------

# Move folder
# Same structure as 'copy', except the command name is 'move'

# -----------------------

# Delete folder or file
"/delete?path=src/components/dash&itemtype=folder"
"/delete?path=src/components/dash.tsx&itemtype=file"

# -----------------------

# Copy content of a file

# line 2 of the dash.tsx is pasted to line 4 of dashboard.tsx shifting existing lines down
"/copycontent?src=src/pages/{dash.tsx}&dest=src/pages/{dashboard.tsx}&lines=2-2&toline=4"
# all lines of the dash.tsx will be appended to dashboard.tsx
"/copycontent?src=src/pages/{dash.tsx}&dest=src/pages/{dashboard.tsx}&lines=1-*&toline=*"
# line 2 to 10 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
"/copycontent?src=src/pages/{dash.tsx}&dest=src/pages/{dashboard.tsx}&lines=2-10&toline=6"
# all lines from line 2 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
"/copycontent?src=src/pages/{dash.tsx}&dest=src/pages/{dashboard.tsx}&lines=2-*&toline=6"
# all lines upto line 10 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
"/copycontent?src=src/pages/{dash.tsx}&dest=src/pages/{dashboard.tsx}&lines=*-10&toline=6"

# Move content of a file
# Same as copy structure, except the command is 'movecontent' instead of 'copycontent'

# Delete content of a file
"/deletecontent?path=src/pages/{dash.tsx}&lines=1-*"
"/deletecontent?path=src/pages/{dash.tsx}&lines=2-2"
"/deletecontent?path=src/pages/{dash.tsx}&lines=4-*"
"/deletecontent?path=src/pages/{dash.tsx}&lines=4-23"
"/deletecontent?path=src/pages/{dash.tsx}&lines=*-23"
