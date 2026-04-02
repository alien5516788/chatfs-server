from time import sleep

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello from sync server"}


@app.get("/command/{name}")
def get_command(name: str):
    sleep(6)
    return {"command": f"You waited for '{name}'"}


@app.get("/code")
def get_code():
    return """
use notify::{Event, RecursiveMode, Result, Watcher};
use std::{path::Path, sync::mpsc};

fn main() -> Result<()> {

    let s = "ssgdg";
    let l = String::from("wehr aoweh ");

    println!("'{} {}'", s.starts_with("ss"), l.trim_start_matches("wet"));

    // Make a channel to receive filesystem events
    let (tx, rx) = mpsc::channel::<notify::Result<Event>>();

    // Create a watcher using the recommended backend for the platform
    let mut watcher = notify::recommended_watcher(tx)?;

    // Add a path to watch (replace "." with the directory you want)
    watcher.watch(Path::new("./src"), RecursiveMode::Recursive)?;

    println!("Watching for changes…");

    // Loop forever, printing events
    for res in rx {
        match res {
            Ok(event) => println!("Event: {:?}", event),
            Err(e) => println!("Watch error: {:?}", e),
        }
    }

    // Note: you usually never reach here
    // because the loop above runs forever
    Ok(())
}
    """
