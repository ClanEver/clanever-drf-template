"""
Something copy from https://github.com/cookiecutter/cookiecutter-django/blob/master/hooks/post_gen_project.py
"""

import os
import random
import re
import string
from pathlib import Path

import tomlkit


def generate_random_string(
    length,
    using_digits=False,
    using_ascii_letters=False,
    using_punctuation=False,
):
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', '\\', '$'}
        suitable = all_punctuation.difference(unsuitable)
        symbols += ''.join(suitable)
    return ''.join([random.choice(symbols) for _ in range(length)])


def set_flag(file_path: Path, flag, value=None, formatted=None, *args, **kwargs):
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your "
                f'system. Please, make sure to manually {flag} later.'
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string

    with file_path.open('r+', encoding='utf-8') as f:
        file_contents = f.read().replace(flag, value)
        f.seek(0)
        f.write(file_contents)
        f.truncate()

    return value


def set_django_secret_key(file_path: Path):
    return set_flag(
        file_path,
        '!!!SET DJANGO_SECRET_KEY!!!',
        length=50,
        using_digits=True,
        using_ascii_letters=True,
        using_punctuation=True,
    )


def set_dependencies_version_in_pyproject():
    try:
        output = os.popen('rye list').read()
        packages = {}
        for line in output.split('\n'):
            match = re.match(r'(\S+)==(\S+)', line)
            if match:
                packages[match.group(1)] = match.group(2)
        if not packages:
            raise OSError('Cannot use rye')

        pyproject_file = Path('pyproject.toml')
        with pyproject_file.open('r') as f:
            pyproject = tomlkit.load(f)

        for idx, raw_dep in enumerate(pyproject['project']['dependencies']):
            if '>=' in raw_dep:
                dep = raw_dep.split('>=')[0]
            elif '~=' in raw_dep:
                dep = raw_dep.split('~=')[0]
            elif '==' in raw_dep:
                dep = raw_dep.split('==')[0]
            else:
                dep = raw_dep
            dep_without_feat = dep.split('[', 1)[0]
            if dep_without_feat in packages:
                pyproject['project']['dependencies'][idx] = f'{dep}~={packages[dep_without_feat]}'

        with pyproject_file.open('w') as f:
            tomlkit.dump(pyproject, f)
    except Exception as e:
        print(f'set dependencies version in pyproject error: {e!r}')


def main():
    production_django_envs_path = Path('{{ cookiecutter.project_slug }}/settings.py')
    set_django_secret_key(production_django_envs_path)
    os.system('rye sync')
    set_dependencies_version_in_pyproject()


if __name__ == '__main__':
    main()
