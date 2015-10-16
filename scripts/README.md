Scripts
=======
Automation for activities from development through deployment.

Script Intentions
-----------------
+ bootstrap: Installs project dependencies
+ cibuild: Configures the environment for testing & then runs `scripts/test`
+ remote_init: Prepares for & then runs `scripts/setup` on a remote server
+ setup: Set up application for the first time after cloning
+ test: Runs the test suite
+ update: Performs migrations and other post-update tasks

Inspiration
-----------
These scripts were inspired by GitHub's "Scripts to Rule Them All" via
[this blog post][STRTA-blog] and [the related GitHub repo][STRTA-repo].

[STRTA-blog]: http://githubengineering.com/scripts-to-rule-them-all/
[STRTA-repo]: https://github.com/github/scripts-to-rule-them-all
