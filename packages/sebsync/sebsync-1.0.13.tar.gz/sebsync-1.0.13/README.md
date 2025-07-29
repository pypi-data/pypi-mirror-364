# Sebsync

The `sebsync` script synchronizes the [Standard Ebooks](https://standardebooks.org/) catalog with
your local EPUB collection.

## How it works

The script reads the Standard Ebooks [OPDS feed](https://standardebooks.org/feeds) and
reconciles the ebooks in their catalog against the EPUBs in your local filesystem,
downloading new ones or updating existing ones as necessary.

If a new ebook is detected in the catalog, then it will be downloaded into your downloads
directory. If an updated version of a book is detected in the catalog that is already in your
local filesystem, then the updated version will be downloaded and stored in the existing local
file.

The script can also display and/or remove outdated and/or deprecated ebooks. A local ebook file
is “deprecated” if its identifier has been replaced by a new identifier in the Standard Ebooks
catalog. This occurs when a book is renamed or substantially revised. Its replacement will be
downloaded as a new ebook.

## Requirements

This script uses Standard Ebooks' OPDS feed to access metadata on all books their catalog. In
order to do so, you need to be a member of the Standard Ebooks
[Patrons Circle](https://standardebooks.org/donate#patrons-circle) (or have previously produced
an ebook for Standard Ebooks). If you're not already a Standard Ebooks patron, please consider
becoming one. It's a tremendously valuable project, deserving of your support.

## Installation

It is easy to install sebsync using [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/stable/):

```
uv tool install sebsync
```
or
```
pipx install sebsync
```

## Example usage

```
sebsync --email addr@example.com --books /home/user/MyBooks --downloads /home/user/MyBooks/Downloads
```

## Questions and answers

Q1. *Why use a separate downloads directory for new ebooks?*

A1. This is a feature for those who want to easily recognize new ebooks, and to manually
rename and/or categorize them within their library. If this feature is not useful for you,
simply set `--downloads` to be the same directory as `--books`.

Q2. *Does this script support Kindle books?*

A2. Not presently. A cursory analysis of the Standard Ebooks AZW3 structure suggests that there
currently isn't a reliable method to reconcile Kindle ebooks with the OPDS feed catalog. If
this feature is important to you, please let us know by voting for
[this issue](https://github.com/pbryan/sebsync/issues/2) in GitHub.
