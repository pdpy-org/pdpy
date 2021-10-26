const vscode = require('vscode');
const path = require('path');


// let _activeTerminal = null;
// vscode.window.onDidCloseTerminal((terminal) => {
//     if (terminal.name === 'pdpy') {
//         if (!terminal.tckDisposed) {
//             disposeTerminal();
//         }
//     }
// });
// function createTerminal() {
//     _activeTerminal = vscode.window.createTerminal('pdpy');
//     return _activeTerminal;
// }
// function disposeTerminal() {
//     _activeTerminal.tckDisposed = true;
//     _activeTerminal.dispose();
//     _activeTerminal = null;
// }
// function getTerminal() {
//     if (!_activeTerminal) {
//         createTerminal();
//     }

//     return _activeTerminal;
// }
// // END TERMINAL

// function resolve(editor, command) {
//     const scPath = vscode.workspace.getConfiguration().get('pdpy.sclangCmd');
//     return command
//         .replace(/\${file}/g, `${editor.document.fileName}`)
//         .replace(/\${sclangCmd}/g, scPath)
// }

// function run(command) {
//     const terminal = getTerminal();

//     terminal.show(true);

//     vscode.commands.executeCommand('workbench.action.terminal.scrollToBottom');
//     terminal.sendText(command, true);
// }

// function warn(msg) {
//     console.log('pdpy.execInTerminal: ', msg)
// }

// function handleInput(editor) {
//     vscode.workspace.saveAll(false);
//     let command = "${sclangCmd} ${file}";
//     const cmd = resolve(
//         editor,
//         command
//     )

//     run(cmd);
// }

// function activate(context) {
//     let execInTerminal = vscode.commands.registerCommand('pdpy.execInTerminal', () => {
//         const editor = vscode.window.activeTextEditor
//         if (!editor) {
//             warn('no active editor');
//             return;
//         }

//         handleInput(editor)
//     });
//     context.subscriptions.push(execInTerminal);

//     let killTerminal = vscode.commands.registerCommand('pdpy.killTerminal', () => {
//         if(_activeTerminal)
//             disposeTerminal();
//     });
//     context.subscriptions.push(killTerminal);
// }
// exports.activate = activate;

// function deactivate() {
//     disposeTerminal();
// }
// exports.deactivate = deactivate;