import os
import sys

if len(sys.argv) != 3:
    print("Usage: python main.py <folder_name>")
    sys.exit(1)

folder_path = sys.argv[1]

if not os.path.isdir(folder_path):
    print(f"Error: '{folder_path}' is not a valid folder")
    sys.exit(1)

output_file = sys.argv[2]

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("structure:\n")
    
    # Print tree structure
    for root, dirs, files in os.walk(folder_path):
        # Skip .git folder entirely
        if '.git' in dirs:
            dirs.remove('.git')
        
        # Sort for consistent order
        dirs.sort()
        files.sort()
        
        depth = root.replace(folder_path, '').count(os.sep)
        indent = " " * 2 * depth
        folder_name = os.path.basename(root) or folder_path
        outfile.write(f"{indent}- {folder_name}\n")
        
        subindent = " " * 2 * (depth + 1)
        for f in files:
            outfile.write(f"{subindent}  - {f}\n")
    
    outfile.write("\n")
    
    # Write file contents
    for root, dirs, files in os.walk(folder_path):
        # Skip .git folder entirely
        if '.git' in dirs:
            dirs.remove('.git')
        
        files.sort()
        for file in files:
            if not file.endswith(".cs"):
                continue
            
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, folder_path)
            
            outfile.write(f"```{rel_path}\n")
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content if content.endswith("\n") else content + "\n")
            except UnicodeDecodeError:
                outfile.write("# Could not read file (binary or encoding issue)\n")
            except Exception as _e:
                outfile.write(f"# Error: {_e}\n")
            outfile.write("```\n\n")

print(f"Done! All files from '{folder_path}' saved to {output_file} 🎉")