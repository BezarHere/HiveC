# HiveCpp

### summary:
A compacted library of variouse tools, useful (at least for me)

### HOW to use
---

### | from the command line you use `py -m hivecpp [, /f, /c] <your arguments>`

<b>if</b> the switch `/f` is used, then all laters arguments should be paths to argument files. this is the only way to execute batch-like builds with multible argument files

<b>otherwise</b>, if the switch `/c` is used or if no switch is used at all, then all the build arguments should be passed into the command line, at the place of `<your arguments>`


EX for the first method:

```
C:\Users\James>py -m hivecpp /f my_args.args
```

the `my_args.args` path is reletive, so it's more like `C:\Users\James\my_args.args`

then you have in your `my_args.args` file (*read the coments*):

```cmake
# the args file supports comments!
# smart argument reading!
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
copy # Arguemnts can be passed one or more values at one line
"__proj__\output\my_lib.lib" "__lib_folder__\lib\lib-64.lib"
/o # this will be parsed as a part of copy

# delete operation (not sure if it will be moved to the trashbin or completly erased)
delete "__proj__\temp"

# adds a new files type to be treated like a header, e.g. copied to the source_output
include_file_type "bat" 
```

### i want the second method, to pass all arguments into the command line!
**Firstly**: just why? it's much cleaner to use a hive args file

**Secondly**: Alrigh, you can pass arguments to the command line, just remove the comments and replace every new line with a space to make the entire file as *one* line (you might need to add `/c` as the first argument)

## Why not CMake?
hivecpp is smaller and easier, given you have (wich most of you have) python installed

# FAQs

### Why can't this be a standalone executable?
becuse a value a transparent script that hides nothing, **but** if you wanted a standalone executable, just make it, there is a lot of tools that can convert a python script(s) to a standalone executable *and don't violate my copyright/licence*

### Where there be support for more languages?
Hopefuly, [contact me](https:\\tweeter.org\BotatoDev) if you want to contribute something

open source doesn't mean open to *all* contributions, any random merge requests will not be accepted.

---

*god bless*