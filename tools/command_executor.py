import subprocess
import pexpect
from rich.console import Console
from rich.panel import Panel

console = Console()

class CommandExecutor:
    @staticmethod
    def execute_command(command, expect_prompts=None, timeout=30):
        console.print()
        console.print(Panel(f"🚀 Execute Command: [bold cyan]{command}[/bold cyan]", 
                           title="🤖 Autonomous Execution", border_style="green"))
        
        try:
            if expect_prompts:
                # Use pexpect for interactive commands
                child = pexpect.spawn(command, encoding='utf-8', timeout=timeout)
                output = ""
                
                for prompt_response in expect_prompts:
                    prompt = prompt_response.get('prompt', '')
                    response = prompt_response.get('response', '')
                    
                    try:
                        child.expect(prompt)
                        output += child.before + prompt
                        child.sendline(response)
                        output += response + '\n'
                    except pexpect.TIMEOUT:
                        output += child.before
                        break
                    except pexpect.EOF:
                        output += child.before
                        break
                
                # Get remaining output
                try:
                    child.expect(pexpect.EOF, timeout=5)
                    output += child.before
                except:
                    output += child.before
                
                returncode = child.exitstatus if child.exitstatus is not None else 0
                return {"stdout": output, "stderr": "", "returncode": returncode}
            else:
                # Use subprocess for non-interactive commands
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
                return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except pexpect.TIMEOUT:
            return {"error": "Command timed out waiting for expected prompt"}
        except Exception as e:
            return {"error": str(e)}
