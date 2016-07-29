# RustAnaconda
A fancy name for a simple wrapper.

## What is this?
This is just a Rust crate that creates a dynamic C compatible shared lib that allows
[AnacondaRUST](https://github.com/DamnWidget/anaconda_rust) to call rustfmt directly from it's Python JsonServer code using
[cFFI](https://pypi.python.org/pypi/cffi) or `ctypes` instead of using subprocesses.

This is also a real world example of how to use CFFI/ctypes to call Rust code from Python code.

## Are you serious?
Yep

## License

```
Copyright 2016 Oscar Campos <damnwidget@gmail.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
