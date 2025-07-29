# collective.collectionepilog

Provides a behavior for collections to add epilog RichText field under the collection results.
The content of the epilog will be added to the collection views via `collection-epilog` viewlet below the content.

## Installation

Install collective.collectionepilog with

`pip`:

```shell
pip install collective.collectionepilog
```

or `uv`:

```shell
uv add collective.collectionepilog
```

## Contribute

- [Issue tracker](https://github.com/collective/collective.collectionepilog/issues)
- [Source code](https://github.com/collective/collective.collectionepilog/)

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)

### Development 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective.collectionepilog
    cd collective.collectionepilog
    ```


### Add features using `plonecli` or `bobtemplates.plone`

This package provides markers as strings (`<!-- extra stuff goes here -->`) that are compatible with [`plonecli`](https://github.com/plone/plonecli) and [`bobtemplates.plone`](https://github.com/plone/bobtemplates.plone).
These markers act as hooks to add all kinds of subtemplates, including behaviors, control panels, upgrade steps, or other subtemplates from `plonecli`.

To run `plonecli` with configuration to target this package, run the following command.

```shell
plonecli add <template_name>
```

For example, you can add a content type to your package with the following command.

```shell
plonecli add content_type
```

You can add a behavior with the following command.

```shell
plonecli add behavior
```

```{seealso}
You can check the list of available subtemplates in the [`bobtemplates.plone` `README.md` file](https://github.com/plone/bobtemplates.plone/?tab=readme-ov-file#provided-subtemplates).
See also the documentation of [Mockup and Patternslib](https://6.docs.plone.org/classic-ui/mockup.html) for how to build the UI toolkit for Classic UI.
```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

A special thanks to all contributors and supporters!
