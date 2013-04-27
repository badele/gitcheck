# gitcheck

=========

Tool to check your repository in a single pass. If you working in multiples projects, the gitcheck script scan recursive directory to find .git directory and analyse git repository status

## Examples utilizations

### Simple version
This version show a summary of your git repositories, it print if you have a repository that have modified. For each lines, it print repository status and if modified, it print number files added and deleted.

```bash
>garchdeps.py
```
![Gitcheck simple](http://bruno.adele.im/static/gitcheck.png)



### Verbose version
Substantially identical to the previous version, in bonus, it print who files modified

```bash
>garchdeps.py -v 
```
![Gitcheck verbose](http://bruno.adele.im/static/gitcheck_verbose.png)

### French version
http://bruno.adele.im/projets/gitcheck/
