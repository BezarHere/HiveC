# HiveCpp

### summary:
A compacted library of variouse tools, useful (at least for me)

### HOW to use

### | from the command line you use `py -m hivecpp [, /f, /c] <your arguments>`

<b>if</b> the switch `/f` is used, then all laters arguments should be paths to argument files. this is the only way to execute batch-like builds with multible argument files

<b>otherwise</b>, if the switch `/c` is used or if no switch is used at all, then all the build arguments should be passed into the command line, at the place of `<your arguments>`


EX for the first method:

```
C:\Users\James>py -m hivecpp /f my_args.args
```

the `my_args.args` path is reletive, so it's more like `C:\Users\James\my_args.args`

then you have in your `my_args.args` file:

```cmake
# the args file supports comments!
# but not single qouts :(

# the project path
project "C:\Users\James\Desktop\MyProject"

# the source folder, '__proj__' will be replaced by the 'project' path
source "__proj__\src"

# the output for all headers in the source folder
source_output "C:\Users\James\Documents\MyLib\include"

# defining a macro with name 'lib_folder' that will replace every '__lib_folder__'
define:lib_folder "C:\Users\James\Documents\MyLib"

# copy operation, '/o' at the end so it will overwrite the destination
copy "__proj__\output\my_lib.lib" "__lib_folder__\lib\lib-64.lib" /o
# delete operation (not sure if it will be moved to the trashbin or completly erased)
delete "__proj__\temp"

# adds a new files type to be treated like a header, e.g. copied to the source_output
include_file_type "bat" 
```

### i want the second method, to pass all arguments into the command line!
**Firstly**: thats why? it's much cleaner in an args file

**Secondly**: Alrigh, you can pass arguments to the command line, just remove the comments and replace every new line with a space to make the entire file as *one* line

## Why not CMake?
hivecpp is some much smaller and easier, given you have (wich most of you have) python installed
