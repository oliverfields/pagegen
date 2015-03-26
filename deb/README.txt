1. Ensure version correct in pagegen file

2. Create git tag
   $ git tag -a <tag> -m '<describe tag>'

3. Push tag
   $ git push origin <tag>

4. Build deb
   $ mkdir <build dir>
   $ ./build <tag> <build dir>

If need to delete remote tag:
$ git tag -d <tag>
$ git push origin :refs/tags/</tag>
