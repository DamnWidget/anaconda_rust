# AnacondaRUST

AnacondaRust offers auto completion, auto formatting and linting for Rust language that will never freeze your Sublime Text 3

## Supported Platforms

AnacondaRUST has been tested in *GNU/Linux*, *OS X* and *Windows 10* with excellent results, take into account that this plugin
is in a very early state and probably there are bugs to fix and things to improve. The current status in the different platforms
is:

| OS | Status |
| --- | --- |
| **GNU/Linux** | stable |
| **OS X** | stable |
| **Windows** | stable |

## Dependencies

1. [Anaconda](https://github.com/DamnWidget/anaconda) plugin for Sublime Text 3
2. Rust compiler ([rustc](https://www.rust-lang.org/)) and cargo
3. [Racer](https://github.com/phildawes/racer) code completion
4. [rustfmt](https://github.com/rust-lang-nursery/rustfmt) >= 0.5.0 code formatter
5. Rust standard lib sources

## Installation

If [Anaconda](https://github.com/DamnWidget/anaconda) is not already installed you must install it using the `Command Palette`,
if it's already installed just skip to the [Install Rustc](https://github.com/DamnWidget/anaconda_rust#install-rust) section.

### Install Anaconda

1. Show the Command Palette (`Cmd + Shift + P` on OS X or `Ctrl + Shift + P` on Linux/Windows)
2. Type `install`, then select `Package Control: Install package` from the options list
3. Type `anaconda` and press `Enter`

### Install Rust

If you have `rustc` and `cargo` already installed in your system, skip to the [Install Racer](https://github.com/DamnWidget/anaconda_rust#install-racer)
section.

There are too many ways to install rust in different operating systems, the following is just a general overview, please,
refer to the [Rust Language Site](https://www.rust-lang.org/) for details about how to install it in case that you have
doubts.

#### GNU/Linux and OS X

We can simply install rust in GNU/Linux and OS X by copying and pasting the following command in a terminal:

`curl -sSf https://static.rust-lang.org/rustup.sh | sh`

The command above will download and install the last stable rust version into your `/usr/local/` directory (you may need root access
to do so).

*Note*: All major GNU/Linux distributions offer *rust* as a pre-compiled binary in their package manager systems, you can install it
using your distribution package manager if you want, whatever works for you should be fine.

#### Windows 10 (probably others are fine)

The easiest way to install rust in Windows is by downloading the Windows binary installers (.msi) from https://www.rust-lang.org/downloads.html
take into account that there are two different versions of the C/C++ Application Binary Interface (ABI) one for GNU and other for MSVC
which one to pick is a very important decision as it will determine if you can compile Rust code that binds with C or C++ libraries
in your system (for example rust-crypto).

It is important to understand that to compile some rust packages that includes some C bindings you need to install a compiler that
generates binaries with a compatible ABI with your rust compiler ABI. That means install [MinGW/MSYS2 toolchain](https://msys2.github.io/) or
[Microsoft Visual C++ Build Tools](http://go.microsoft.com/fwlink/?LinkId=691126) (or alternatively [Visual Studio](https://www.visualstudio.com/downloads/)
and select the C++ tools during installation)

##### How can I choose my ABI?

Simple, if you use [MinGW/MSYS2 toolchain](https://msys2.github.io/) to compile C and C++ code in your Windows just download the GNU ABI version of the installer,
otherwise you should download the MSVC version as probably all the applications and libraries in your Windows are compiled using some
version of the Microsoft Visual C++ compiler.

### Install Racer

If racer is already installed in your system just skip to the [Install rustfmt](https://github.com/DamnWidget/anaconda_rust#install-rustfmt)
section. Racer is easily installed using `cargo` as:

```bash
cargo install racer
```

That will download all the source code, compile and install racer into your cargo binary directory, cargo is great.

### Install rustfmt

If rustfmt is already installed in your system just skip to the [Install AnacondaRUST](https://github.com/DamnWidget/anaconda_rust#install-anacondarust)
section. rustfmt is easily installed using `cargo` as:

```bash
cargo install rustfmt
```

The command above will download compile and install `rustfmt` in your system, again, cargo is great.

*Note*: install `rustfmt` 0.5.0 or better for a smoothly integration, older versions give problems when used in anaconda_rust

### Install AnacondaRUST

To install AnacondaRUST you just need to follow the steps below:

1. Show the Command Palette (`Cmd + Shift + P` on OS X or `Ctrl + Shift + P` on Linux/Windows)
2. Type `install` then select `Package Control: Install package` from the options list
3. Type `anaconda_rust` and press `Enter`

## Configure AnacondaRUST

Anaconda **could** work out of the box if rustc, racer and rustfmt are available in your `PATH`, you already downloaded the rust source
code and the environment variable `RUST_SRC_PATH` is set to the path where your rust source code is downloaded to, that would be a
perfect scenario that probably is not gonna happen so read carefully the steps below in order to make your AnacondaRUST works.

### Download Rust Source Code

You may be wondering why I want you to download Rust source code if you already installed rust in the previous section, the reason is
simple, `racer` needs access to the rust's source code to be able to offer auto completion for the rust's standard library. The Rust
sources can be downloaded from their site https://www.rust-lang.org/downloads.html just download the source for the same version that
you already installed in your system.

### Configure Binary Paths

Open AnacondaRUST configuration using `Preferences -> Package Settings -> AnacondaRUST` and set the path to your `racer` and `rustfmt`
binaries. For example:

```json

{
	"rustc_binary_path": "/usr/bin/rustc",
	"racer_binary_path": "/home/damnwidget/.cargo/bin/racer",
	"rustfmt_binary_path": "/home/damnwidget/.cargo/bin/rustfmt"
}
```

### Configure Rust Source Code Path

Now you need to tell AnacondaRUST where your copy of the Rust's source code lives in your system, add the path to your AnacondaRUST
configuration like:

```json
...
	"rust_src_path": "/home/damnwidget/downloads/languages/rust/sources/1.8.0/src",
```

Set the `RUST_SRC_PATH` environment variable and leeaving the `rust_src_path` config empty may work in Operating Systems where the
environment vars are passed to the Sublime Text 3 executable, sadly this doesn't always work so I really recommend to set your
AnacondaRUST settings to prevent future problems.

## Linter Options

AnacondaRUST (obviously) includes a linter for Rust code, the linter runs asynchronous as usual, it runs every time that you save your file.

### Disable the linter

AnacondaRUST linter is enabled by default, it can be totally disabled setting `anaconda_rust_linting` to `false` in the configuration.

### Goto Definition

AnacondaRUST includes a Goto Definition feature but it does not add key bindings by default. You can access the `Goto Rust Definition`
feature through the `Command Palette`, anyway, if you want to add a key binding for it you could use something like:

```json
{
	"command": "rust_goto", "keys": ["ctrl+r", "ctrl+g"], "context": [
		{"key": "selector", "operator": "equal", "operand": "source.rust"}
	]
}
```

### Show Documentation

If racer 1.2.10 or higher is installed, anacondaRUST can offer documentation using the `Control Palette` or the `Contextual Menu`, you
can also add a shortcut like:

```json
{
	"command": "rust_doc", "keys": ["ctrl+r", "ctrl+d"], "context": [
		{"key": "selector", "operator": "eual", "operan": "source.rust"}
	]
}
```

## License

As usual for all my Sublime Text plugins, this software is licensed under the [GPLv3](https://github.com/DamnWidget/anaconda_rust/blob/master/LICENSE) terms.


## Donations

Please donate to help keep this project alive.

[![PayPal][paypal-donate-image]][paypal-donate-link]

[paypal-donate-image]: https://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif
[paypal-donate-link]: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=KP7PAHR962UGG&lc=US&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHosted
