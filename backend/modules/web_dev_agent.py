"""
WebDevAgent - Specialized AI agent for web development and fixing website issues

This module provides a high-performance AI agent specifically designed for:
1. Diagnosing and fixing HTML/CSS/JavaScript issues
2. Optimizing website performance
3. Implementing modern web technologies
4. Ensuring cross-browser compatibility
5. Fixing responsive design issues
6. Handling authentication systems (Google, GitHub, etc.)

The agent uses a modular architecture allowing it to work independently
or as part of the dual agent system.
"""

import json
import re
import os
from typing import Dict, List, Tuple, Any, Union, Optional

class WebDevAgent:
    """
    Specialized AI agent for web development tasks and website fixing
    """
    
    def __init__(self, debug_mode: bool = False):
        """
        Initialize the WebDevAgent with optional debug mode
        
        Args:
            debug_mode: If True, provides verbose logging and step-by-step analysis
        """
        self.debug_mode = debug_mode
        self.supported_file_types = [
            'html', 'css', 'js', 'jsx', 'ts', 'tsx', 'json', 'svg'
        ]
        self.issue_registry = self._build_issue_registry()
        
    def _build_issue_registry(self) -> Dict:
        """
        Build a comprehensive registry of common web development issues and their solutions
        
        Returns:
            Dictionary mapping issue patterns to solution strategies
        """
        return {
            # HTML Issues
            "malformed_html": {
                "patterns": [
                    r"<([a-z]+)[^>]*>[^<]*</\1>",  # Unclosed tags
                    r"<([a-z]+)[^>]*>[^<]*<\/(?!\1)[a-z]+>"  # Mismatched tags
                ],
                "solutions": ["Fix tag nesting", "Ensure proper tag closure"]
            },
            
            # CSS Issues
            "responsive_issues": {
                "patterns": [
                    r"width:\s*\d+px",  # Fixed width elements
                    r"@media"  # Check for missing media queries
                ],
                "solutions": ["Convert fixed widths to relative units", "Add responsive breakpoints"]
            },
            
            # JavaScript Issues
            "js_errors": {
                "patterns": [
                    r"console\.log\(",  # Debug code left in production
                    r"(document\.getElementById|querySelector)\(['\"][^'\"]*['\"]\)\.(innerHTML|outerHTML)"  # Potential XSS
                ],
                "solutions": ["Remove debug statements", "Use safer DOM manipulation methods"]
            },
            
            # Authentication Issues
            "auth_issues": {
                "patterns": [
                    r"google\.accounts\.id\.initialize",  # Google Sign-In
                    r"gapi\.auth2"  # Older Google Sign-In
                ],
                "solutions": ["Update to latest Google Identity Services", "Fix callback handling"]
            },
            
            # Performance Issues
            "performance_issues": {
                "patterns": [
                    r"document\.querySelector\(['\"][^'\"]*['\"]\)",  # Repeated DOM queries
                    r"for\s*\(\s*let\s+[a-zA-Z_$][0-9a-zA-Z_$]*\s*=\s*0"  # Potentially inefficient loops
                ],
                "solutions": ["Cache DOM queries", "Optimize loops with appropriate methods"]
            }
        }
    
    def analyze_website(self, directory_path: str) -> Dict[str, Any]:
        """
        Analyze a website directory to identify issues and suggest improvements
        
        Args:
            directory_path: Path to the website's root directory
            
        Returns:
            Comprehensive analysis with issues and recommendations
        """
        files = self._get_web_files(directory_path)
        analysis = {
            "total_files_analyzed": len(files),
            "issues_found": 0,
            "critical_issues": 0,
            "warnings": 0,
            "file_analysis": {},
            "overall_recommendations": []
        }
        
        # Analyze each file
        for file_path in files:
            file_analysis = self.analyze_file(file_path)
            analysis["file_analysis"][file_path] = file_analysis
            
            # Update counts
            analysis["issues_found"] += len(file_analysis["issues"])
            analysis["critical_issues"] += len([i for i in file_analysis["issues"] if i["severity"] == "critical"])
            analysis["warnings"] += len([i for i in file_analysis["issues"] if i["severity"] == "warning"])
        
        # Generate overall recommendations
        if analysis["critical_issues"] > 0:
            analysis["overall_recommendations"].append("Address critical issues first, particularly authentication and security problems")
        
        if self._has_responsive_issues(analysis):
            analysis["overall_recommendations"].append("Implement a comprehensive responsive design strategy")
        
        if self._has_performance_issues(analysis):
            analysis["overall_recommendations"].append("Consider performance optimization techniques")
            
        return analysis
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single web file for issues
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Analysis of the file with issues and recommendations
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except Exception as e:
            return {
                "error": f"Could not read file: {str(e)}",
                "issues": [],
                "recommendations": []
            }
        
        file_ext = file_path.split('.')[-1].lower()
        
        analysis = {
            "file_type": file_ext,
            "file_size_bytes": len(content),
            "issues": [],
            "recommendations": []
        }
        
        # Check for common issues based on file type
        if file_ext == 'html':
            self._analyze_html(content, analysis)
        elif file_ext == 'css':
            self._analyze_css(content, analysis)
        elif file_ext in ['js', 'jsx', 'ts', 'tsx']:
            self._analyze_js(content, analysis)
        
        # Generate file-specific recommendations
        if len(analysis["issues"]) > 0:
            issue_types = set([issue["type"] for issue in analysis["issues"]])
            for issue_type in issue_types:
                if issue_type in self.issue_registry:
                    for solution in self.issue_registry[issue_type]["solutions"]:
                        if solution not in analysis["recommendations"]:
                            analysis["recommendations"].append(solution)
        
        return analysis
    
    def _analyze_html(self, content: str, analysis: Dict[str, Any]) -> None:
        """
        Analyze HTML content for issues
        
        Args:
            content: HTML content as string
            analysis: Analysis dict to update with findings
        """
        # Check for unclosed tags
        unclosed_tags = re.findall(r"<([a-z]+)[^>]*>(?!.*</\1>)", content)
        if unclosed_tags:
            analysis["issues"].append({
                "type": "malformed_html",
                "severity": "critical",
                "description": f"Unclosed HTML tags: {', '.join(unclosed_tags)}"
            })
        
        # Check for accessibility issues
        if '<img' in content and not re.search(r'<img[^>]*alt=["\''][^"\']*["\'"]', content):
            analysis["issues"].append({
                "type": "accessibility",
                "severity": "warning",
                "description": "Images missing alt attributes"
            })
        
        # Check for responsive meta tag
        if not re.search(r'<meta[^>]*name=["\'"]viewport["\'"]', content):
            analysis["issues"].append({
                "type": "responsive_issues",
                "severity": "warning",
                "description": "Missing viewport meta tag for responsive design"
            })
            
        # Check for Google Sign-In implementation
        if 'google.accounts.id.initialize' in content:
            if not re.search(r'google\.accounts\.id\.renderButton', content):
                analysis["issues"].append({
                    "type": "auth_issues",
                    "severity": "critical",
                    "description": "Google Sign-In initialization present but renderButton is missing"
                })
    
    def _analyze_css(self, content: str, analysis: Dict[str, Any]) -> None:
        """
        Analyze CSS content for issues
        
        Args:
            content: CSS content as string
            analysis: Analysis dict to update with findings
        """
        # Check for fixed width elements
        fixed_width_count = len(re.findall(r"width:\s*\d+px", content))
        if fixed_width_count > 3:  # Some fixed widths are OK, but too many suggest responsive issues
            analysis["issues"].append({
                "type": "responsive_issues",
                "severity": "warning",
                "description": f"Found {fixed_width_count} fixed-width elements that may cause responsive design issues"
            })
        
        # Check for browser prefixes
        if not re.search(r"-webkit-|-moz-|-ms-", content) and re.search(r"flex|grid|transform", content):
            analysis["issues"].append({
                "type": "compatibility",
                "severity": "warning",
                "description": "Modern CSS properties used without vendor prefixes"
            })
        
        # Check for media queries
        if '@media' not in content:
            analysis["issues"].append({
                "type": "responsive_issues",
                "severity": "warning",
                "description": "No media queries found for responsive design"
            })
    
    def _analyze_js(self, content: str, analysis: Dict[str, Any]) -> None:
        """
        Analyze JavaScript content for issues
        
        Args:
            content: JavaScript content as string
            analysis: Analysis dict to update with findings
        """
        # Check for console.log statements
        console_logs = len(re.findall(r"console\.log\(", content))
        if console_logs > 0:
            analysis["issues"].append({
                "type": "js_errors",
                "severity": "warning",
                "description": f"Found {console_logs} console.log statements that should be removed in production"
            })
        
        # Check for potential memory leaks
        event_listeners = len(re.findall(r"addEventListener\(", content))
        event_removals = len(re.findall(r"removeEventListener\(", content))
        if event_listeners > event_removals + 2:  # Allow some disparity
            analysis["issues"].append({
                "type": "performance_issues",
                "severity": "warning",
                "description": f"Potential memory leak: {event_listeners} event listeners added but only {event_removals} removed"
            })
        
        # Check for Google Sign-In implementation
        if 'google.accounts.id.initialize' in content:
            if not re.search(r'callback:\s*\w+', content):
                analysis["issues"].append({
                    "type": "auth_issues",
                    "severity": "critical",
                    "description": "Google Sign-In missing callback configuration"
                })
    
    def _get_web_files(self, directory_path: str) -> List[str]:
        """
        Get all web-related files from a directory
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of file paths for web-related files
        """
        web_files = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.split('.')[-1].lower() in self.supported_file_types:
                    web_files.append(os.path.join(root, file))
        return web_files
    
    def _has_responsive_issues(self, analysis: Dict[str, Any]) -> bool:
        """Check if the website has responsive design issues"""
        for file_analysis in analysis["file_analysis"].values():
            for issue in file_analysis.get("issues", []):
                if issue["type"] == "responsive_issues":
                    return True
        return False
    
    def _has_performance_issues(self, analysis: Dict[str, Any]) -> bool:
        """Check if the website has performance issues"""
        for file_analysis in analysis["file_analysis"].values():
            for issue in file_analysis.get("issues", []):
                if issue["type"] == "performance_issues":
                    return True
        return False
        
    def fix_issues(self, analysis: Dict[str, Any], auto_fix: bool = False) -> Dict[str, Any]:
        """
        Fix issues identified in the analysis
        
        Args:
            analysis: Analysis dict from analyze_website
            auto_fix: If True, automatically applies fixes where possible
            
        Returns:
            Report of fixes applied or suggested
        """
        fix_report = {
            "files_modified": 0,
            "issues_fixed": 0,
            "issues_requiring_manual_fix": 0,
            "fixes": {}
        }
        
        for file_path, file_analysis in analysis["file_analysis"].items():
            if not file_analysis.get("issues"):
                continue
                
            file_fixes = []
            manual_fixes = []
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                modified_content = content
                
                # Apply fixes based on issue type
                for issue in file_analysis["issues"]:
                    if issue["type"] == "malformed_html":
                        fixed, modified_content = self._fix_malformed_html(modified_content)
                        if fixed:
                            file_fixes.append(f"Fixed {issue['description']}")
                        else:
                            manual_fixes.append(f"Manual fix needed: {issue['description']}")
                    
                    elif issue["type"] == "responsive_issues":
                        fixed, modified_content = self._fix_responsive_issues(modified_content)
                        if fixed:
                            file_fixes.append(f"Fixed {issue['description']}")
                        else:
                            manual_fixes.append(f"Manual fix needed: {issue['description']}")
                    
                    elif issue["type"] == "js_errors":
                        fixed, modified_content = self._fix_js_errors(modified_content)
                        if fixed:
                            file_fixes.append(f"Fixed {issue['description']}")
                        else:
                            manual_fixes.append(f"Manual fix needed: {issue['description']}")
                    
                    elif issue["type"] == "auth_issues":
                        fixed, modified_content = self._fix_auth_issues(modified_content)
                        if fixed:
                            file_fixes.append(f"Fixed {issue['description']}")
                        else:
                            manual_fixes.append(f"Manual fix needed: {issue['description']}")
                
                # Write fixes if auto_fix is enabled and changes were made
                if auto_fix and content != modified_content:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(modified_content)
                    fix_report["files_modified"] += 1
                
                fix_report["issues_fixed"] += len(file_fixes)
                fix_report["issues_requiring_manual_fix"] += len(manual_fixes)
                
                fix_report["fixes"][file_path] = {
                    "automatic_fixes": file_fixes,
                    "manual_fixes": manual_fixes
                }
                
            except Exception as e:
                if self.debug_mode:
                    print(f"Error fixing {file_path}: {str(e)}")
                fix_report["fixes"][file_path] = {
                    "error": str(e),
                    "automatic_fixes": [],
                    "manual_fixes": [f"Failed to process file: {str(e)}"]
                }
        
        return fix_report
        
    def _fix_malformed_html(self, content: str) -> Tuple[bool, str]:
        """Fix malformed HTML issues"""
        fixed = False
        
        # Simple fix for unclosed tags
        unclosed_tags = re.findall(r"<([a-z]+)[^>]*>(?!.*</\1>)", content)
        modified_content = content
        
        for tag in unclosed_tags:
            if tag in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                # Self-closing tags should have /> at the end
                pattern = r"<" + tag + r"([^>]*)(?<!\/)>"
                replacement = r"<" + tag + r"\1 />"
                modified_content = re.sub(pattern, replacement, modified_content)
                fixed = True
            else:
                # Regular tags need a closing tag
                pattern = r"<" + tag + r"([^>]*)>(?!.*</\1>)"
                replacement = r"<" + tag + r"\1>CONTENT_NEEDS_REVIEW</" + tag + r">"
                # This is a simplistic approach, would need more advanced parsing for real fixes
                if re.search(pattern, modified_content):
                    modified_content = re.sub(pattern, replacement, modified_content, count=1)
                    fixed = True
        
        return fixed, modified_content

    def _fix_responsive_issues(self, content: str) -> Tuple[bool, str]:
        """Fix responsive design issues"""
        fixed = False
        modified_content = content
        
        # Add viewport meta tag if missing (for HTML)
        if '<head>' in modified_content and not re.search(r'<meta[^>]*name=["\'"]viewport["\'"]', modified_content):
            modified_content = modified_content.replace(
                '<head>',
                '<head>\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
            )
            fixed = True
        
        # Convert fixed widths to relative units (for CSS)
        if re.search(r"width:\s*\d+px", modified_content):
            # Replace only widths that are not for borders, shadows, etc.
            modified_content = re.sub(
                r"(^|\s)width:\s*(\d+)px\b",
                lambda m: f"{m.group(1)}width: {float(m.group(2))/16}rem" if int(m.group(2)) > 5 else m.group(0),
                modified_content
            )
            fixed = True
        
        return fixed, modified_content

    def _fix_js_errors(self, content: str) -> Tuple[bool, str]:
        """Fix JavaScript issues"""
        fixed = False
        modified_content = content
        
        # Remove console.log statements
        if re.search(r"console\.log\(", modified_content):
            modified_content = re.sub(r"\s*console\.log\([^;]*\);", "", modified_content)
            fixed = True
        
        # Add event listener removal for potential memory leaks
        pattern = r"(\w+)\.addEventListener\(['\"](\w+)['\"],\s*(\w+)"
        matches = re.findall(pattern, modified_content)
        
        for element, event, handler in matches:
            # Check if there's already a corresponding removeEventListener
            if not re.search(fr"{element}\.removeEventListener\(['\"]?{event}['\"]?,\s*{handler}", modified_content):
                # Look for potential cleanup functions like componentWillUnmount, useEffect cleanup, etc.
                cleanup_patterns = [
                    r"componentWillUnmount\s*\(\s*\)\s*{([^}]*)}",
                    r"useEffect\s*\(\s*\(\s*\)\s*=>\s*{[^}]*return\s*\(\s*\)\s*=>\s*{([^}]*)}"
                ]
                
                for cleanup_pattern in cleanup_patterns:
                    cleanup_match = re.search(cleanup_pattern, modified_content)
                    if cleanup_match:
                        cleanup_code = cleanup_match.group(1)
                        # Add removeEventListener to cleanup if not already there
                        if f"{element}.removeEventListener" not in cleanup_code:
                            new_cleanup = cleanup_code + f"\n    {element}.removeEventListener('{event}', {handler});"
                            modified_content = modified_content.replace(cleanup_code, new_cleanup)
                            fixed = True
                            break
        
        return fixed, modified_content

    def _fix_auth_issues(self, content: str) -> Tuple[bool, str]:
        """Fix authentication issues, particularly for Google Sign-In"""
        fixed = False
        modified_content = content
        
        # Fix Google Sign-In initialization missing renderButton
        if 'google.accounts.id.initialize' in modified_content and 'google.accounts.id.renderButton' not in modified_content:
            # Look for a typical container element
            container_pattern = r"document\.getElementById\(['\"](\w+)['\"]\)"
            container_match = re.search(container_pattern, modified_content)
            
            if container_match:
                container_id = container_match.group(1)
                init_pattern = r"(google\.accounts\.id\.initialize\s*\([^)]+\);)"
                
                render_code = f"""
    // Render the Google Sign-In button
    google.accounts.id.renderButton(
      document.getElementById("{container_id}"),
      {{ type: "standard", theme: "outline", size: "large" }}
    );"""
                
                if re.search(init_pattern, modified_content):
                    modified_content = re.sub(
                        init_pattern,
                        r"\1" + render_code,
                        modified_content
                    )
                    fixed = True
        
        # Fix missing callback in Google Sign-In initialization
        if 'google.accounts.id.initialize' in modified_content and not re.search(r'callback:\s*\w+', modified_content):
            # First check if there's a handler function already defined
            handler_pattern = r"function\s+(\w+Response|handleCredential|authCallback)\s*\("
            handler_match = re.search(handler_pattern, modified_content)
            
            handler_name = "handleCredentialResponse"
            if handler_match:
                handler_name = handler_match.group(1)
            else:
                # Add a handler function if none exists
                handler_code = """
    function handleCredentialResponse(response) {
      if (response.credential) {
        console.log("Google authentication successful");
        // Process the credential here
      }
    }
"""
                # Insert before the initialize call
                init_index = modified_content.find("google.accounts.id.initialize")
                if init_index > 0:
                    prev_line_end = modified_content.rfind("}", init_index) + 1
                    if prev_line_end > 0:
                        modified_content = (
                            modified_content[:prev_line_end] + 
                            handler_code + 
                            modified_content[prev_line_end:]
                        )
            
            # Now add the callback parameter to initialize
            if not re.search(r'callback:', modified_content):
                modified_content = re.sub(
                    r"(google\.accounts\.id\.initialize\s*\(\s*{)",
                    r"\1\n      callback: " + handler_name + ",",
                    modified_content
                )
                fixed = True
        
        return fixed, modified_content
    
    def optimize_website(self, directory_path: str) -> Dict[str, Any]:
        """
        Perform website optimization across all files
        
        Args:
            directory_path: Path to the website's root directory
            
        Returns:
            Optimization report with improvements made
        """
        report = {
            "optimizations_applied": 0,
            "estimated_performance_gain": "0%",
            "file_optimizations": {}
        }
        
        # First analyze to find issues
        analysis = self.analyze_website(directory_path)
        
        # Apply specific optimizations
        html_optimized = self._optimize_html_files(directory_path)
        css_optimized = self._optimize_css_files(directory_path)
        js_optimized = self._optimize_js_files(directory_path)
        image_optimized = self._optimize_image_references(directory_path)
        
        total_optimizations = sum([
            len(html_optimized["files"]),
            len(css_optimized["files"]),
            len(js_optimized["files"]),
            len(image_optimized["files"])
        ])
        
        report["optimizations_applied"] = total_optimizations
        report["file_optimizations"] = {
            "html": html_optimized,
            "css": css_optimized,
            "javascript": js_optimized,
            "images": image_optimized
        }
        
        # Estimate performance gain based on optimization count
        if total_optimizations > 20:
            report["estimated_performance_gain"] = "30-40%"
        elif total_optimizations > 10:
            report["estimated_performance_gain"] = "15-25%"
        elif total_optimizations > 5:
            report["estimated_performance_gain"] = "5-15%"
        else:
            report["estimated_performance_gain"] = "1-5%"
            
        return report
    
    def _optimize_html_files(self, directory_path: str) -> Dict[str, Any]:
        """Optimize HTML files"""
        optimization = {
            "files": {},
            "total_bytes_saved": 0
        }
        
        html_files = [f for f in self._get_web_files(directory_path) if f.endswith('.html')]
        
        for file_path in html_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                original_size = len(content)
                
                # Remove comments (except conditional comments for IE)
                modified_content = re.sub(r"<!--(?!<!)[^\[>].*?-->", "", content)
                
                # Remove unnecessary whitespace (simplistic approach)
                modified_content = re.sub(r">\s+<", "><", modified_content)
                
                # Remove unnecessary attributes
                modified_content = re.sub(r'\s+type="text/javascript"', '', modified_content)
                modified_content = re.sub(r'\s+type="text/css"', '', modified_content)
                
                # Write optimized file
                if len(modified_content) < original_size:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(modified_content)
                    
                    bytes_saved = original_size - len(modified_content)
                    optimization["total_bytes_saved"] += bytes_saved
                    optimization["files"][file_path] = {
                        "original_size": original_size,
                        "optimized_size": len(modified_content),
                        "bytes_saved": bytes_saved
                    }
            except Exception as e:
                if self.debug_mode:
                    print(f"Error optimizing HTML file {file_path}: {str(e)}")
        
        return optimization
    
    def _optimize_css_files(self, directory_path: str) -> Dict[str, Any]:
        """Optimize CSS files"""
        optimization = {
            "files": {},
            "total_bytes_saved": 0
        }
        
        css_files = [f for f in self._get_web_files(directory_path) if f.endswith('.css')]
        
        for file_path in css_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                original_size = len(content)
                
                # Remove comments
                modified_content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
                
                # Remove unnecessary whitespace
                modified_content = re.sub(r"\s*{\s*", "{", modified_content)
                modified_content = re.sub(r"\s*}\s*", "}", modified_content)
                modified_content = re.sub(r"\s*;\s*", ";", modified_content)
                modified_content = re.sub(r"\s*:\s*", ":", modified_content)
                
                # Write optimized file
                if len(modified_content) < original_size:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(modified_content)
                    
                    bytes_saved = original_size - len(modified_content)
                    optimization["total_bytes_saved"] += bytes_saved
                    optimization["files"][file_path] = {
                        "original_size": original_size,
                        "optimized_size": len(modified_content),
                        "bytes_saved": bytes_saved
                    }
            except Exception as e:
                if self.debug_mode:
                    print(f"Error optimizing CSS file {file_path}: {str(e)}")
        
        return optimization
    
    def _optimize_js_files(self, directory_path: str) -> Dict[str, Any]:
        """Optimize JavaScript files (basic optimization only)"""
        optimization = {
            "files": {},
            "total_bytes_saved": 0
        }
        
        js_files = [f for f in self._get_web_files(directory_path) if f.endswith(('.js', '.jsx'))]
        
        for file_path in js_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                original_size = len(content)
                
                # Remove comments (simplistic approach - would use terser in production)
                modified_content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
                modified_content = re.sub(r"/\*.*?\*/", "", modified_content, flags=re.DOTALL)
                
                # Remove console.log statements
                modified_content = re.sub(r"\s*console\.log\([^;]*\);", "", modified_content)
                
                # Write optimized file
                if len(modified_content) < original_size:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(modified_content)
                    
                    bytes_saved = original_size - len(modified_content)
                    optimization["total_bytes_saved"] += bytes_saved
                    optimization["files"][file_path] = {
                        "original_size": original_size,
                        "optimized_size": len(modified_content),
                        "bytes_saved": bytes_saved
                    }
            except Exception as e:
                if self.debug_mode:
                    print(f"Error optimizing JS file {file_path}: {str(e)}")
        
        return optimization
    
    def _optimize_image_references(self, directory_path: str) -> Dict[str, Any]:
        """Optimize image references in HTML and CSS files"""
        optimization = {
            "files": {},
            "total_optimizations": 0
        }
        
        html_files = [f for f in self._get_web_files(directory_path) if f.endswith('.html')]
        css_files = [f for f in self._get_web_files(directory_path) if f.endswith('.css')]
        
        for file_path in
