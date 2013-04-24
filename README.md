# gitcheck

=========

Tool to check your repository in a single pass. If you working in multiples projects, the gitcheck script scan recursive directory to find .git directory and analyse git repository status

## Examples utilizations

### Simple version
This version show a summary of your git repositories, it print if you have a repository that have modified. For each lines, it print repository status and if modified, it print number files added and deleted.

```bash
>garchdeps.py
gitcheck  
cacause  [Modifify:2 / Delete:0]
fabrecipes  
garchdeps  [Modifify:1 / Delete:0]
garchdeps/distrib/archlinux/src/garchdeps  
garchdeps/distrib/archlinux/src/garchdeps-build  
blog.jesuislibre.org  
informemoi  
old-projects  
fabtools  
bruno.adele.im  
rstblog  [Modifify:1 / Delete:0]
wanted  [Modifify:1 / Delete:0]
kdoors_to_delete  
www.cendreo.com  
blog.cendreo.com  
memorykey  
```
![Gitcheck simple](http://bruno.adele.im/static/gitcheck.png)



### Verbose version
Substantially identical to the previous version, in bonus, it print who files modified

```bash
>garchdeps.py -v 
gitcheck  
cacause  [Modifify:2 / Delete:0]
|--Server/templates/add.html
|--Server/templates/layout.html
fabrecipes  
garchdeps  [Modifify:1 / Delete:0]
|--garchdeps.py
garchdeps/distrib/archlinux/src/garchdeps  
garchdeps/distrib/archlinux/src/garchdeps-build  
blog.jesuislibre.org  
informemoi  
old-projects  
fabtools  
bruno.adele.im  
rstblog  [Modifify:1 / Delete:0]
|--rstblog/templates/rst_display.html
wanted  [Modifify:1 / Delete:0]
|--wanted.py
kdoors_to_delete  
www.cendreo.com  
blog.cendreo.com  
memorykey  
```
![Gitcheck verbose](http://bruno.adele.im/static/gitcheck_verbose.png)
