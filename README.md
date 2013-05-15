# gitcheck

=========

If you working in multiples projects, you want can be analyzed in a single pass of the changes in your projects. gitcheck is script who scan recursive directory to find a git directory and analyse all modifications.

## Examples utilizations

### Simple version
In simple version, it show for each repositories if you have modification not committed and or commits not pushed.

```bash
>garchdeps.py
```
![Gitcheck simple](http://bruno.adele.im/static/gitcheck.png)



### Verbose version
Substantially identical to the previous version, in bonus, it print who files modified and commits not pushed

```bash
>garchdeps.py -v 
```
![Gitcheck verbose](http://bruno.adele.im/static/gitcheck_verbose.png)

### Options

```plaintext
-v, --verbose                     Show files & commits
-r, --remote                      also check with the remote
-i <re>, --ignore-branch <re>     ignore branches matching the regex <re>
```


### French version is available here
http://bruno.adele.im/projets/gitcheck/
