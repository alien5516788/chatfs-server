from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()


@router.get("/home")
def home():
    return RedirectResponse(url="/")


@router.get("/")
def server():
    return HTMLResponse("""
    <html>

    <h2> QuerySync Server </h2>
    <pre>
    - This server provides file system access and content retrieval for a connected client.
    - User must manually obtain a codebase url from client tool and send it to the chat.
    - Client Id uniquely identifies the local codebase that LLM is dealing with.
    - e.g:

        https://servername.com/fad3e27b21f7400/
         ^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^
            Base url              Client Id

    - The codebase status can be checked by directly fetching the codebase url.
    - e.g:

        https://servername.com/fad3e27b21f7400/

    - You as the LLM must use below query system appended with the codebase url to craft the full request.
    - e.g:

        https://servername.com/fad3e27b21f7400/list?path=&recursive=false&itemtype=file
    </pre>

    <h2> Available capabilities </h2>
    <pre>
    <h3> List directory </h3>

    /list?path=&recursive=false&itemtype=all        # list all in root
    /list?path=&recursive=true&itemtype=all         # list all in root recursively
    /list?path=&recursive=false&itemtype=file       # list all files in root
    /list?path=&recursive=true&itemtype=file        # list all files in root recursively
    /list?path=&recursive=false&itemtype=folder     # list all directories in root
    /list?path=&recursive=true&itemtype=folder      # list all directories in root recursively

    /list?path=src&recursive=false&itemtype=all     # list all in root/src
    /list?path=src&recursive=true&itemtype=all      # list all in root/src recursively
    /list?path=src&recursive=false&itemtype=file    # list all files in root/src
    /list?path=src&recursive=true&itemtype=file     # list all files in root/src recursively
    /list?path=src&recursive=false&itemtype=folder  # list all directories in root/src
    /list?path=src&recursive=true&itemtype=folder   # list all directories in root/src recursively

    <h3> File content </h3>

    /content?path=src/dash.ts&lines=3-3   # line 3
    /content?path=src/dash.ts&lines=1-*   # all lines
    /content?path=src/dash.ts&lines=3-*   # all lines from line 3
    /content?path=src/dash.ts&lines=1-23  # line 1 to line 23 # if only 20 lines avaible 23 is taken as 20
    /content?path=src/dash.ts&lines=*-20  # all lines upto line 20

    <h3> Create folder or file </h3>

    /create?path=src/components&itemtype=folder
    /create?path=src/dash.ts&itemtype=file

    <h3> Rename folder or file </h3>

    /rename?path=src/components&newname=ui&itemtype=folder
    /rename?path=src/pages/dash.tsx&newname=dashboard.tsx&itemtype=file

    <h3> Copy folder or file </h3>

    /copy?src=src/components&dest=src/ui&itemtype=folder    # new folder will be src/ui/components
    /copy?src=src/pages/dash.tsx&dest=src/ui&itemtype=file  # new file will be src/ui/dash.tsx

    <h3> Move folder </h3>

    # Same structure as 'copy' structure, except the command name is 'move'

    <h3> Delete folder or file </h3>

    /delete?path=src/components/dash&itemtype=folder
    /delete?path=src/components/dash.tsx&itemtype=file

    <h3> Copy content of a file </h3>

    # line 2 of the dash.tsx is pasted to line 4 of dashboard.tsx shifting existing lines down
    /copycontent?src=src/pages/dash.tsx&dest=src/pages/dashboard.tsx&lines=2-2&toline=4

    # all lines of the dash.tsx will be appended to dashboard.tsx
    /copycontent?src=src/pages/dash.tsx&dest=src/pages/dashboard.tsx&lines=1-*&toline=*

    # line 2 to 10 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
    /copycontent?src=src/pages/dash.tsx&dest=src/pages/dashboard.tsx&lines=2-10&toline=6

    # all lines from line 2 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
    /copycontent?src=src/pages/dash.tsx&dest=src/pages/dashboard.tsx&lines=2-*&toline=6

    # all lines upto line 10 of the dash.tsx is pasted to line 6 of dashboard.tsx shifting existing content down
    /copycontent?src=src/pages/dash.tsx&dest=src/pages/dashboard.tsx&lines=*-10&toline=6

    <h3> Move content of a file </h3>

    Same structure as 'copycontent' structure, except the command name is 'movecontent'

    <h3> Delete content of a file </h3>

    /deletecontent?path=src/pages/dash.tsx&lines=1-*
    /deletecontent?path=src/pages/dash.tsx&lines=2-2
    /deletecontent?path=src/pages/dash.tsx&lines=4-*
    /deletecontent?path=src/pages/dash.tsx&lines=4-23
    /deletecontent?path=src/pages/dash.tsx&lines=*-23

    <h3> Write content to a file </h3>

    Write content actions is not supported directly becuase of LLM limitations
    </pre>

    <h2> Rules and constraints </h2>
    <pre>
    - All paths are restricted to the server working directory (e.g. "" or ".")
    - If path, folder or file names contain url unsafe chars, url-encode them before crafting url
    - Directory traversal outside the root is not allowed (e.g. "./../")
    - Ignore rules may exclude certain files or folders
    - Binary or unreadable files return a readable error message
    - Directory paths cannot be used with the content tool
    </pre>

    <h2> Response format </h2>
    <pre>
    - All responses follow a minimal structure:
    - e.g:

      {
        "status": boolean,           # Wheather the request was successful or not
        "arbitrary_fields": string   # Any LLM firendly info regarding the request or retrieved info
      }
    </pre>

    <h2> Notes </h2>
    <pre>
    - Paths are always relative
    - Line ranges are 1-based and inclusive
    - If requested lines exceed file length, they are clamped
    - If a folder path is incorrect then it falls back to root ('' or '.')
    </pre>

    <p> Do a great collab with your new super power </p>

    </html>
""")
