# Django `INSTALLED_APPS` Precedence Test

## Background
By accident, we realised that we have no way to know if the order of
INSTALLED_APPS (in Django config) is unexpectedly overriding a
resource that we intended to use with one we didn't intend to use.

From [Django official docs on INSTALLED_APPS settings](https://docs.djangoproject.com/en/1.8/ref/settings/#installed-apps):
```
When several applications provide different versions of the same
resource (template, static file, management command, translation), the
application listed first in INSTALLED_APPS has precedence.
```
So, it would be nice to have a test, which could check all templates
and report potential conflicts unless we can verify that it is
resolved CORRECTLY.

Annnnnd, there we go. :-)

## Usage
Download `precedence_test.py` and put it in `localAppFolder/management/commands`.

Run
```bash
./manage.py precedence_test | grep CONFLICT
```
and hopefully you can see the potential conflicts (´∀｀*)
