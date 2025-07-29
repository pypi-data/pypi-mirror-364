from setuptools import setup, find_packages, Command
from setuptools.command.install import install
import os
import sys
import site
from pathlib import Path
import subprocess

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        # Now that the package is installed, try to update PATH
        try:
            # Get the bin directory where scripts are installed
            if site.check_enableusersite():
                bin_dir = site.getuserbase() + "/bin"
            else:
                bin_dir = Path(sys.prefix) / "bin"
            
            # Detect the user's shell
            shell = os.environ.get('SHELL', '')
            if shell:
                shell_name = os.path.basename(shell)
                
                if shell_name == 'bash':
                    rc_file = os.path.expanduser('~/.bashrc')
                    profile_file = os.path.expanduser('~/.bash_profile')
                elif shell_name == 'zsh':
                    rc_file = os.path.expanduser('~/.zshrc')
                    profile_file = rc_file
                else:
                    print(f"Unsupported shell: {shell_name}. Please add {bin_dir} to your PATH manually.")
                    return
                
                # Add the bin directory to the PATH in the shell config files
                path_line = f'\n# Added by remote-detector package\nexport PATH="{bin_dir}:$PATH"\n'
                
                try:
                    with open(rc_file, 'a') as f:
                        f.write(path_line)
                    
                    # Also add to profile if it exists and is different from rc_file
                    if os.path.exists(profile_file) and profile_file != rc_file:
                        with open(profile_file, 'a') as f:
                            f.write(path_line)
                    
                    print(f"Added {bin_dir} to PATH in {rc_file}")
                    
                    # Try to source the file immediately for current session
                    try:
                        if shell_name == 'bash':
                            os.system(f"source {rc_file} 2>/dev/null || true")
                        elif shell_name == 'zsh':
                            os.system(f"source {rc_file} 2>/dev/null || true")
                    except:
                        pass
                    
                    print(f"✅ Installation complete! You may need to restart your terminal or run 'source {rc_file}'")
                    print(f"   to use the 'remote-detector' command immediately.")
                except Exception as e:
                    print(f"Failed to update PATH: {e}")
                    print(f"Please add {bin_dir} to your PATH manually.")
            
            # On Windows, update the PATH in registry
            if os.name == 'nt':
                try:
                    import winreg
                    with winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER) as root:
                        with winreg.OpenKey(root, "Environment", 0, winreg.KEY_ALL_ACCESS) as key:
                            existing_path, _ = winreg.QueryValueEx(key, "PATH")
                            if str(bin_dir) not in existing_path:
                                new_path = f"{existing_path};{bin_dir}"
                                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                                print(f"Added {bin_dir} to Windows PATH.")
                                # Notify the system about the PATH change
                                subprocess.call(['setx', 'PATH', new_path])
                                print("✅ Installation complete! You may need to restart your terminal to use the 'remote-detector' command.")
                except Exception as e:
                    print(f"Failed to update Windows PATH: {e}")
                    print(f"Please add {bin_dir} to your PATH manually.")
                
        except Exception as e:
            print(f"Error during post-install: {e}")
            print(f"You may need to manually add the script directory to your PATH.")

setup(
    name="remote-detector",
    version="0.1.2",
    author="Akshay Waghmare",
    author_email="your.email@example.com",
    description="Detects remote access tools and logs ERP login to MongoDB.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/remote-detector",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "psutil",
        "click",
        "python-json-logger",
        "requests",
        "beautifulsoup4",
        "pymongo"
    ],
    entry_points={
        "console_scripts": [
            "remote-detector = remote_detector.cli:cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security",
        "Topic :: Utilities"
    ],
    python_requires='>=3.7',
    project_urls={
        "Bug Reports": "https://github.com/yourusername/remote-detector/issues",
        "Source": "https://github.com/yourusername/remote-detector",
    },
    keywords="remote access, monitoring, security, erp, detection",
    cmdclass={
        'install': PostInstallCommand,
    },
) 