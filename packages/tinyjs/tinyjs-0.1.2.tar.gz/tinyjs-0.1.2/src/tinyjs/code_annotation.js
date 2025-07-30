import fs from 'fs'
import path from 'path'
import vm from 'vm'
import { argv } from 'process'


const input_path = argv[2]
const output_path = input_path.replace('temp_input.json', 'temp_output.json')
const error_path = input_path.replace('temp_input.json', 'error.log')


const runIsolated = (code) => {
    const captured = [];
    const sandbox = {
        console: {
            log: (...args) => {
                captured.push(...args);
            },
            info: (...args) => {
                captured.push(...args);
            }
        }
    };
    const ctx = vm.createContext(sandbox);
    try {
        vm.runInContext(code, ctx);
    } catch (error) {
        fs.writeFileSync(error_path, `Error executing code: ${error.message}\nCode:\n${code}`, { flag: 'a' });
        return false 
    }
    return captured;
}

const errorLogPath = path.join('output', 'error.log');
if (fs.existsSync(errorLogPath)) {
    fs.unlinkSync(errorLogPath);
}


const programs = JSON.parse(fs.readFileSync(input_path, 'utf8'))

const new_programs = programs.map(program => {
    const code = program.script
    
    const captured = runIsolated(code);

    if (!captured) return;
    return {
        ...program,
        output: '# ' + captured.join('\n# ')
    }
}).filter(program => program !== undefined);

console.log(programs.length - new_programs.length, 'programs were dropped');

fs.writeFileSync(output_path, JSON.stringify(new_programs, null, 4), 'utf8')