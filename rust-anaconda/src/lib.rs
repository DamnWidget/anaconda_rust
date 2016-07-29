// Copyright 2016 Oscar Campos <damnwidget@gmail.com>
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

extern crate libc;
extern crate racer;
extern crate rustfmt;

use libc::{c_char, uint32_t};

use rustfmt::{Input, Summary, run};
use rustfmt::config::{Config, WriteMode};

use racer::core;
use racer::scopes;
use racer::core::Match;

use std::thread;
use std::{env, error};
use std::fs::{self, File};
use std::process::{Command, Stdio};
use std::ffi::{CString, CStr};
use std::path::{Path, PathBuf};
use std::io::{ErrorKind, Read, Write};

// rustfmt related
type FmtError = Box<error::Error + Send + Sync>;
type FmtResult<T> = std::result::Result<T, FmtError>;

fn match_cli_path_or_file(config_path: Option<PathBuf>,
                          input_file: &Path)
                          -> FmtResult<(Config, Option<PathBuf>)> {

    if let Some(config_file) = config_path {
        let (toml, path) = try!(resolve_config(config_file.as_ref()));
        if path.is_some() {
            return Ok((toml, path));
        }
    }
    resolve_config(input_file)
}

fn resolve_config(dir: &Path) -> FmtResult<(Config, Option<PathBuf>)> {
    let path = try!(lookup_project_file(dir));
    if path.is_none() {
        return Ok((Config::default(), None));
    }
    let path = path.unwrap();
    let mut file = try!(File::open(&path));
    let mut toml = String::new();
    try!(file.read_to_string(&mut toml));
    Ok((Config::from_toml(&toml), Some(path)))
}

fn lookup_project_file(dir: &Path) -> FmtResult<Option<PathBuf>> {
    let mut current = if dir.is_relative() {
        try!(env::current_dir()).join(dir)
    } else {
        dir.to_path_buf()
    };

    current = try!(fs::canonicalize(current));

    loop {
        let config_file = current.join("rustfmt.toml");
        match fs::metadata(&config_file) {
            // Only return if it's a file to handle the unlikely situation of a directory named
            // `rustfmt.toml`.
            Ok(ref md) if md.is_file() => return Ok(Some(config_file)),
            // Return the error if it's something other than `NotFound`; otherwise we didn't find
            // the project file yet, and continue searching.
            Err(e) => {
                if e.kind() != ErrorKind::NotFound {
                    return Err(FmtError::from(e));
                }
            }
            _ => {}
        }

        // If the current directory has no parent, we're done searching.
        if !current.pop() {
            return Ok(None);
        }
    }
}

pub fn rustfmt(buffer: String, cfg_path: Option<String>) -> i32 {
    let config_path: Option<PathBuf> = cfg_path
        .map(PathBuf::from)
        .and_then(|dir| {
            if dir.is_file() {
                return dir.parent().map(|v| v.into());
            }
            Some(dir)
        });

    // try to read config from local directory
    let (mut config, _) = match_cli_path_or_file(config_path, &env::current_dir().unwrap())
        .expect("Error resolving config");

    // write_mode is alwais Plain for anaconda_rust
    config.write_mode = WriteMode::Plain;

    // run the command and return status code
    process_summary(run(Input::Text(buffer), &config))
}

fn process_summary(error_summary: Summary) -> i32 {
    let status_code: i32;
    if error_summary.has_operational_errors() {
        status_code = 1
    } else if error_summary.has_parsing_errors() {
        status_code = 2
    } else if error_summary.has_formatting_errors() {
        status_code = 3
    } else {
        assert!(error_summary.has_no_errors());
        status_code = 0
    }

    // flush standard output
    std::io::stdout().flush().unwrap();
    // return the excution code
    status_code
}

// racer related
fn racer_complete(code: String, path_str: String, line: usize, offset: usize) -> String {
    // We can not allow rust from panicking or the Python
    // process spawned by ST3 will die and die is sad.
    //
    // To prevent it we fire the call to the underlying
    // libracer wrapped into a thread so we can catch
    // any panic and response with an error
    let child = thread::spawn(move || {
        let mut output = String::new();
        let cache = core::FileCache::new();
        let path_buf = PathBuf::from(path_str);
        let path = path_buf.as_path();
        let session = core::Session::from_path(&cache, path, path);

        // cache the contents of the given file path and code
        cache.cache_file_contents(path, code);

        let src = session.load_file(path);
        let point = scopes::coords_to_point(&src, line, offset);

        for m in core::complete_from_file(&src, path, point, &session) {
            output = format!("{}\n{}", output, match_fn(m, &session));
        }
        output

    });
    match child.join() {
        Ok(v) => format!("{}", v),
        Err(e) => format!("error\tRacer Panicked: {:?}", e)
    }
}

fn find_definition(code: String, path_str: String, line: usize, offset: usize) -> String {
    let child = thread::spawn(move || {
        let path_buf = PathBuf::from(path_str);
        let path = path_buf.as_path();
        let cache = core::FileCache::new();
        let session = core::Session::from_path(&cache, path, path);

        // cache the contents of the given file path and code
        cache.cache_file_contents(path, code);

        let src = session.load_file(path);
        let pos = scopes::coords_to_point(&src, line, offset);

        match  core::find_definition(&src, path, pos, &session) {
            Some(m) => match_definition(m, &session),
            None => String::new(),
        }
    });
    match child.join() {
        Ok(v) => format!("{}", v),
        Err(e) => format!("error\tRacer Panicked: {:?}", e)
    }
}

fn get_documentation(code: String, path_str: String, line: usize, offset: usize) -> String {
    let child = thread::spawn(move || {
        let cache = core::FileCache::new();
        let path_buf = PathBuf::from(path_str);
        let path = path_buf.as_path();
        let session = core::Session::from_path(&cache, path, path);

        // cache the contents of the given file path and code
        cache.cache_file_contents(path, code);

        let src = session.load_file(path);
        let point = scopes::coords_to_point(&src, line, offset);

        let mut matches = core::complete_from_file(&src, path, point, &session);
        match_doc_fn(matches.next().unwrap())
    });
    match child.join() {
        Ok(v) => format!("{}", v),
        Err(e) => format!("error\tRacer Panicked: {:?}", e)
    }
}

fn match_fn(m: Match, session: &core::Session) -> String {
    if m.matchstr == "" {
        String::from("MATCHSTR is empty - waddup?");
    }

    let snippet = racer::snippets::snippet_for_match(&m, session);
    format!("{}\t{}\t{}\t{:?}\t{}",
            m.matchstr,
            snippet,
            m.filepath.to_str().unwrap(),
            m.mtype,
            m.contextstr.replace("\t", "\\t"),
    )
}

fn match_definition(m: Match, session: &core::Session) -> String {
    let (linenum, offset) = scopes::point_to_coords_from_file(&m.filepath, m.point, session).unwrap();
    if m.matchstr == "" {
        String::from("MATCHSTR is empty - waddup?");
    }

    format!("{}\t{}\t{}", m.filepath.to_str().unwrap(), linenum.to_string(), offset.to_string())
}

fn match_doc_fn(m: Match) -> String {
    if m.matchstr == "" {
        String::from("MATCHSTR is mepty - waddup?");
    }

    format!("{:?}", m.docs)
}

// FFI related

/// This function converts a C char * string into a safe Rust String
/// It assures that the c_str is not null using assert! macro so you
/// must be certain that yo never pass null strings to any of the
/// exported functions
fn c_str_to_safe_string(c_str: *const libc::c_char) -> String {
    unsafe {
        assert!(!c_str.is_null());
        CStr::from_ptr(c_str).to_string_lossy().into_owned()
    }
}

/// Converts a Rust String into a C char * and returns a pointer
/// to it's inner memory
///
/// WARNING: this function forgets about the allocated memory so
/// YOU MUST MAKE SURE to delete this memory yourself, there is
/// a convenience exported function to do that, you can just
/// call `free_c_char_mem` with the C string as parameter to
/// free the allocated memory from your C compatible code
fn to_c_str(s: String) -> *mut c_char {
    let c_string = CString::new(s).unwrap();
    c_string.into_raw()
}

/// Get the value of the given environment key
///
/// WARNING: this function forgets about the allocated memory so
/// YOU MUST MAKE SURE to delete this memory yourself
#[no_mangle]
pub extern fn get_env(key: *const c_char) -> *mut c_char {
    let k = c_str_to_safe_string(key);
    match env::var(&k) {
        Ok(val) => to_c_str(val),
        Err(e) => to_c_str(format!("while getting env key {}: {}", k, e))
    }
}

/// Return this crate version as a C string
///
/// NOTE: You should free the allocated string memory after is not need anymore
#[no_mangle]
pub extern fn get_version() -> *mut c_char {
    to_c_str(String::from(option_env!("CARGO_PKG_VERSION").unwrap_or("unknown")))
}

/// This function can be used to free memory allocated by Rust
///
/// You can also free the memory in your C compatible app calling
/// the stdlib free function for example
#[no_mangle]
pub extern fn free_c_char_mem(c: *mut c_char) {
    unsafe {
        if c.is_null() { return }
        CString::from_raw(c)
    };
}

/// Format the passed buffer using librustfmt and return back an operation
/// status code, librustfmt uses the standard output to print the formating
/// results so we are forced to call our own compiled binary and capture its
/// standard output.
///
/// No memory need to be freed after use this function as it is automatically
/// handled by Rust itself
#[no_mangle]
pub extern fn format(bin_path: *const c_char, code: *const c_char, path: *const c_char) -> *mut c_char {
    let config_path = c_str_to_safe_string(path);
    let buffer = c_str_to_safe_string(code);
    let bpath = c_str_to_safe_string(bin_path);
    let p = match Command::new(&bpath)
                             .arg(config_path)
                             .stdin(Stdio::piped())
                             .stderr(Stdio::piped())
                             .stdout(Stdio::piped())
                             .spawn() {
        Err(why) => panic!("could not spawn {} because of {}", bpath, why),
        Ok(process) => process
    };

    p.stdin.unwrap().write_all(buffer.as_bytes()).unwrap();
    let mut buffer = String::new();
    match p.stdout.unwrap().read_to_string(&mut buffer) {
        Err(why) => panic!("could not read stdout: {}", why),
        Ok(_) => {},
    };
    to_c_str(buffer)
}

/// Look for code completions using libracer and return back a string with
/// a result per line with fields separated by tabs (\t)
///
/// WARNING: this function forgets about the allocated memory so
/// YOU MUST MAKE SURE to delete this memory yourself.
#[no_mangle]
pub extern fn complete(code: *const c_char, path: *const c_char, line: uint32_t, col: uint32_t) -> *mut c_char {
    to_c_str(racer_complete(c_str_to_safe_string(code), c_str_to_safe_string(path), line as usize, col as usize))
}

/// Look for definitions of the word under the cursor using libracer and
/// return a string with a result per line with fields separated by tabs
///
/// WARNING: this function forgets about the allocated memory so
/// YOU MUST MAKE SURE to delete this memory yourself
#[no_mangle]
pub extern fn definitions(code: *const c_char, path: *const c_char, line: uint32_t, col: uint32_t) -> *mut c_char {
    to_c_str(find_definition(c_str_to_safe_string(code), c_str_to_safe_string(path), line as usize, col as usize))
}

/// Look for documentation about the word under the cursor using libracer
/// and return a string with a result per line with fields separated by tabs
///
/// WARNING: this function forgets about the allocated memory so
/// YOU MUST MAKE SURE to delete this memory yourself.
#[no_mangle]
pub extern fn documentation(code: *const c_char, path: *const c_char, line: uint32_t, col: uint32_t) -> *mut c_char {
    to_c_str(get_documentation(c_str_to_safe_string(code), c_str_to_safe_string(path), line as usize, col as usize))
}

