"""
Accessibility compliance utilities for production deployment.

This module provides:
1. Accessibility compliance checking
2. WCAG 2.1 guidelines implementation
3. Automated accessibility testing
4. Accessibility report generation
5. Remediation suggestions
"""

import os
import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from functools import wraps

from bs4 import BeautifulSoup

from utils.logger import setup_logger

# Set up module logger
logger = setup_logger('utils.accessibility')

# ===== Accessibility Configuration =====

class AccessibilityConfig:
    """Accessibility configuration settings."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize accessibility configuration."""
        self.config = config or {}
        
        # WCAG compliance level
        self.wcag_level = self.config.get('wcag_level', 'AA')  # A, AA, or AAA
        
        # Features to check
        self.check_alt_text = self.config.get('check_alt_text', True)
        self.check_color_contrast = self.config.get('check_color_contrast', True)
        self.check_form_labels = self.config.get('check_form_labels', True)
        self.check_aria_attributes = self.config.get('check_aria_attributes', True)
        self.check_heading_hierarchy = self.config.get('check_heading_hierarchy', True)
        self.check_link_text = self.config.get('check_link_text', True)
        
        # Reporting
        self.generate_reports = self.config.get('generate_reports', False)
        self.report_path = self.config.get('report_path', './accessibility_reports')
        
        # Automated testing
        self.run_automated_tests = self.config.get('run_automated_tests', False)
        self.test_urls = self.config.get('test_urls', [])
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        config = {
            'wcag_level': os.environ.get('ACCESSIBILITY_WCAG_LEVEL', 'AA'),
            'check_alt_text': os.environ.get('ACCESSIBILITY_CHECK_ALT_TEXT', 'true').lower() == 'true',
            'check_color_contrast': os.environ.get('ACCESSIBILITY_CHECK_COLOR_CONTRAST', 'true').lower() == 'true',
            'check_form_labels': os.environ.get('ACCESSIBILITY_CHECK_FORM_LABELS', 'true').lower() == 'true',
            'check_aria_attributes': os.environ.get('ACCESSIBILITY_CHECK_ARIA', 'true').lower() == 'true',
            'check_heading_hierarchy': os.environ.get('ACCESSIBILITY_CHECK_HEADINGS', 'true').lower() == 'true',
            'check_link_text': os.environ.get('ACCESSIBILITY_CHECK_LINK_TEXT', 'true').lower() == 'true',
            'generate_reports': os.environ.get('ACCESSIBILITY_GENERATE_REPORTS', 'false').lower() == 'true',
            'report_path': os.environ.get('ACCESSIBILITY_REPORT_PATH', './accessibility_reports'),
            'run_automated_tests': os.environ.get('ACCESSIBILITY_RUN_AUTOMATED_TESTS', 'false').lower() == 'true',
        }
        
        # Parse test URLs if provided
        test_urls_str = os.environ.get('ACCESSIBILITY_TEST_URLS', '')
        if test_urls_str:
            config['test_urls'] = [url.strip() for url in test_urls_str.split(',')]
        
        return cls(config)

# ===== Accessibility Issue =====

class AccessibilityIssue:
    """Accessibility issue representation."""
    
    def __init__(self, code: str, message: str, element: Optional[str] = None,
                severity: str = 'error', wcag_criterion: Optional[str] = None,
                remediation: Optional[str] = None):
        """Initialize accessibility issue."""
        self.code = code
        self.message = message
        self.element = element
        self.severity = severity  # error, warning, info
        self.wcag_criterion = wcag_criterion
        self.remediation = remediation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            'code': self.code,
            'message': self.message,
            'element': self.element,
            'severity': self.severity,
            'wcag_criterion': self.wcag_criterion,
            'remediation': self.remediation
        }

# ===== WCAG Guidelines =====

WCAG_GUIDELINES = {
    # Perceivable
    '1.1.1': {
        'name': 'Non-text Content',
        'description': 'All non-text content has a text alternative',
        'level': 'A'
    },
    '1.3.1': {
        'name': 'Info and Relationships',
        'description': 'Information, structure, and relationships can be programmatically determined',
        'level': 'A'
    },
    '1.4.3': {
        'name': 'Contrast (Minimum)',
        'description': 'Text has sufficient contrast against its background',
        'level': 'AA'
    },
    '1.4.6': {
        'name': 'Contrast (Enhanced)',
        'description': 'Text has enhanced contrast against its background',
        'level': 'AAA'
    },
    
    # Operable
    '2.1.1': {
        'name': 'Keyboard',
        'description': 'All functionality is available from a keyboard',
        'level': 'A'
    },
    '2.4.4': {
        'name': 'Link Purpose (In Context)',
        'description': 'The purpose of each link can be determined from the link text or context',
        'level': 'A'
    },
    '2.4.6': {
        'name': 'Headings and Labels',
        'description': 'Headings and labels describe topic or purpose',
        'level': 'AA'
    },
    
    # Understandable
    '3.3.2': {
        'name': 'Labels or Instructions',
        'description': 'Labels or instructions are provided for user input',
        'level': 'A'
    },
    
    # Robust
    '4.1.2': {
        'name': 'Name, Role, Value',
        'description': 'For all UI components, the name, role, and value can be programmatically determined',
        'level': 'A'
    }
}

# ===== Accessibility Checkers =====

def check_alt_text(html: str) -> List[AccessibilityIssue]:
    """Check for missing alt text on images.
    
    Args:
        html: HTML content to check
        
    Returns:
        List of accessibility issues
    """
    issues = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check images
    for img in soup.find_all('img'):
        if not img.get('alt'):
            issues.append(AccessibilityIssue(
                code='missing-alt',
                message='Image missing alt text',
                element=str(img)[:100] + ('...' if len(str(img)) > 100 else ''),
                severity='error',
                wcag_criterion='1.1.1',
                remediation='Add descriptive alt text to the image'
            ))
        elif img.get('alt') == '':
            # Empty alt is valid for decorative images, but let's flag it as info
            issues.append(AccessibilityIssue(
                code='empty-alt',
                message='Image has empty alt text (acceptable for decorative images)',
                element=str(img)[:100] + ('...' if len(str(img)) > 100 else ''),
                severity='info',
                wcag_criterion='1.1.1',
                remediation='Ensure this image is truly decorative'
            ))
    
    return issues

def check_form_labels(html: str) -> List[AccessibilityIssue]:
    """Check for form inputs without associated labels.
    
    Args:
        html: HTML content to check
        
    Returns:
        List of accessibility issues
    """
    issues = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check form inputs
    for input_tag in soup.find_all('input'):
        # Skip hidden inputs and submit/button inputs
        input_type = input_tag.get('type', '').lower()
        if input_type in ['hidden', 'submit', 'button', 'image']:
            continue
        
        # Check for id attribute
        input_id = input_tag.get('id')
        if not input_id:
            issues.append(AccessibilityIssue(
                code='input-no-id',
                message=f'Input ({input_type}) has no id attribute for label association',
                element=str(input_tag)[:100] + ('...' if len(str(input_tag)) > 100 else ''),
                severity='error',
                wcag_criterion='3.3.2',
                remediation='Add an id attribute to the input and associate it with a label'
            ))
            continue
        
        # Check for associated label
        label = soup.find('label', attrs={'for': input_id})
        if not label:
            # Check if input is inside a label
            parent_label = input_tag.find_parent('label')
            if not parent_label:
                issues.append(AccessibilityIssue(
                    code='input-no-label',
                    message=f'Input ({input_type}) with id "{input_id}" has no associated label',
                    element=str(input_tag)[:100] + ('...' if len(str(input_tag)) > 100 else ''),
                    severity='error',
                    wcag_criterion='3.3.2',
                    remediation='Add a label element with a for attribute matching the input id'
                ))
    
    # Check select elements
    for select in soup.find_all('select'):
        select_id = select.get('id')
        if not select_id:
            issues.append(AccessibilityIssue(
                code='select-no-id',
                message='Select element has no id attribute for label association',
                element=str(select)[:100] + ('...' if len(str(select)) > 100 else ''),
                severity='error',
                wcag_criterion='3.3.2',
                remediation='Add an id attribute to the select and associate it with a label'
            ))
            continue
        
        # Check for associated label
        label = soup.find('label', attrs={'for': select_id})
        if not label:
            # Check if select is inside a label
            parent_label = select.find_parent('label')
            if not parent_label:
                issues.append(AccessibilityIssue(
                    code='select-no-label',
                    message=f'Select with id "{select_id}" has no associated label',
                    element=str(select)[:100] + ('...' if len(str(select)) > 100 else ''),
                    severity='error',
                    wcag_criterion='3.3.2',
                    remediation='Add a label element with a for attribute matching the select id'
                ))
    
    # Check textarea elements
    for textarea in soup.find_all('textarea'):
        textarea_id = textarea.get('id')
        if not textarea_id:
            issues.append(AccessibilityIssue(
                code='textarea-no-id',
                message='Textarea has no id attribute for label association',
                element=str(textarea)[:100] + ('...' if len(str(textarea)) > 100 else ''),
                severity='error',
                wcag_criterion='3.3.2',
                remediation='Add an id attribute to the textarea and associate it with a label'
            ))
            continue
        
        # Check for associated label
        label = soup.find('label', attrs={'for': textarea_id})
        if not label:
            # Check if textarea is inside a label
            parent_label = textarea.find_parent('label')
            if not parent_label:
                issues.append(AccessibilityIssue(
                    code='textarea-no-label',
                    message=f'Textarea with id "{textarea_id}" has no associated label',
                    element=str(textarea)[:100] + ('...' if len(str(textarea)) > 100 else ''),
                    severity='error',
                    wcag_criterion='3.3.2',
                    remediation='Add a label element with a for attribute matching the textarea id'
                ))
    
    return issues

def check_heading_hierarchy(html: str) -> List[AccessibilityIssue]:
    """Check for proper heading hierarchy.
    
    Args:
        html: HTML content to check
        
    Returns:
        List of accessibility issues
    """
    issues = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all headings
    headings = []
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            headings.append((i, heading))
    
    # Sort headings by their position in the document
    headings.sort(key=lambda x: soup.get_text().find(x[1].get_text()))
    
    # Check for skipped levels
    prev_level = 0
    for level, heading in headings:
        if prev_level > 0 and level > prev_level + 1:
            issues.append(AccessibilityIssue(
                code='heading-skipped-level',
                message=f'Heading level skipped from H{prev_level} to H{level}',
                element=str(heading)[:100] + ('...' if len(str(heading)) > 100 else ''),
                severity='warning',
                wcag_criterion='1.3.1',
                remediation=f'Use H{prev_level + 1} instead of H{level} or add missing heading levels'
            ))
        prev_level = level
    
    # Check for first heading not being H1
    if headings and headings[0][0] != 1:
        issues.append(AccessibilityIssue(
            code='heading-first-not-h1',
            message=f'First heading is H{headings[0][0]}, not H1',
            element=str(headings[0][1])[:100] + ('...' if len(str(headings[0][1])) > 100 else ''),
            severity='warning',
            wcag_criterion='1.3.1',
            remediation='Start the document with an H1 heading'
        ))
    
    # Check for multiple H1 headings
    h1_count = sum(1 for level, _ in headings if level == 1)
    if h1_count > 1:
        issues.append(AccessibilityIssue(
            code='heading-multiple-h1',
            message=f'Multiple H1 headings found ({h1_count})',
            element=None,
            severity='warning',
            wcag_criterion='1.3.1',
            remediation='Use only one H1 heading per page'
        ))
    
    return issues

def check_link_text(html: str) -> List[AccessibilityIssue]:
    """Check for meaningful link text.
    
    Args:
        html: HTML content to check
        
    Returns:
        List of accessibility issues
    """
    issues = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Problematic link texts
    problematic_texts = [
        'click here', 'click', 'here', 'more', 'read more', 'link',
        'this link', 'learn more', 'details', 'more info'
    ]
    
    for link in soup.find_all('a'):
        # Get link text
        link_text = link.get_text().strip().lower()
        
        # Skip links with no text but with aria-label or title
        if not link_text and (link.get('aria-label') or link.get('title')):
            continue
        
        # Check for empty links
        if not link_text and not link.find('img'):
            issues.append(AccessibilityIssue(
                code='link-empty',
                message='Link has no text content',
                element=str(link)[:100] + ('...' if len(str(link)) > 100 else ''),
                severity='error',
                wcag_criterion='2.4.4',
                remediation='Add descriptive text to the link or use aria-label'
            ))
        
        # Check for problematic link text
        elif link_text in problematic_texts:
            issues.append(AccessibilityIssue(
                code='link-generic-text',
                message=f'Link has generic text: "{link_text}"',
                element=str(link)[:100] + ('...' if len(str(link)) > 100 else ''),
                severity='warning',
                wcag_criterion='2.4.4',
                remediation='Use descriptive text that indicates the link purpose'
            ))
        
        # Check for very short link text
        elif len(link_text) < 4 and not link.find('img'):
            issues.append(AccessibilityIssue(
                code='link-short-text',
                message=f'Link text is very short: "{link_text}"',
                element=str(link)[:100] + ('...' if len(str(link)) > 100 else ''),
                severity='warning',
                wcag_criterion='2.4.4',
                remediation='Use more descriptive link text'
            ))
    
    return issues

def check_aria_attributes(html: str) -> List[AccessibilityIssue]:
    """Check for proper ARIA attribute usage.
    
    Args:
        html: HTML content to check
        
    Returns:
        List of accessibility issues
    """
    issues = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check for invalid role values
    valid_roles = {
        'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
        'cell', 'checkbox', 'columnheader', 'combobox', 'complementary',
        'contentinfo', 'definition', 'dialog', 'directory', 'document',
        'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading',
        'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee',
        'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio',
        'navigation', 'none', 'note', 'option', 'presentation', 'progressbar',
        'radio', 'radiogroup', 'region', 'row', 'rowgroup', 'rowheader',
        'scrollbar', 'search', 'searchbox', 'separator', 'slider', 'spinbutton',
        'status', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term',
        'textbox', 'timer', 'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem'
    }
    
    for element in soup.find_all(attrs={'role': True}):
        role = element.get('role')
        if role not in valid_roles:
            issues.append(AccessibilityIssue(
                code='aria-invalid-role',
                message=f'Invalid ARIA role: "{role}"',
                element=str(element)[:100] + ('...' if len(str(element)) > 100 else ''),
                severity='error',
                wcag_criterion='4.1.2',
                remediation=f'Use a valid ARIA role from the list of allowed values'
            ))
    
    # Check for aria-hidden="true" on focusable elements
    focusable_selectors = ['a', 'button', 'input', 'select', 'textarea', '[tabindex]']
    for selector in focusable_selectors:
        for element in soup.select(selector):
            if element.get('aria-hidden') == 'true':
                issues.append(AccessibilityIssue(
                    code='aria-hidden-focusable',
                    message='aria-hidden="true" used on a focusable element',
                    element=str(element)[:100] + ('...' if len(str(element)) > 100 else ''),
                    severity='error',
                    wcag_criterion='4.1.2',
                    remediation='Remove aria-hidden from focusable elements or make them non-focusable'
                ))
    
    # Check for required ARIA attributes
    elements_with_role = soup.find_all(attrs={'role': True})
    for element in elements_with_role:
        role = element.get('role')
        
        # Elements with role="checkbox" or role="radio" should have aria-checked
        if role in ['checkbox', 'radio', 'switch'] and 'aria-checked' not in element.attrs:
            issues.append(AccessibilityIssue(
                code='aria-missing-state',
                message=f'Element with role="{role}" is missing aria-checked attribute',
                element=str(element)[:100] + ('...' if len(str(element)) > 100 else ''),
                severity='error',
                wcag_criterion='4.1.2',
                remediation=f'Add aria-checked attribute to the {role} element'
            ))
        
        # Elements with role="combobox" should have aria-expanded
        if role == 'combobox' and 'aria-expanded' not in element.attrs:
            issues.append(AccessibilityIssue(
                code='aria-missing-state',
                message='Element with role="combobox" is missing aria-expanded attribute',
                element=str(element)[:100] + ('...' if len(str(element)) > 100 else ''),
                severity='error',
                wcag_criterion='4.1.2',
                remediation='Add aria-expanded attribute to the combobox element'
            ))
    
    return issues

# ===== Accessibility Checker =====

class AccessibilityChecker:
    """Accessibility compliance checker."""
    
    def __init__(self, config: Optional[AccessibilityConfig] = None):
        """Initialize accessibility checker."""
        self.config = config or AccessibilityConfig()
    
    def check_html(self, html: str) -> List[AccessibilityIssue]:
        """Check HTML content for accessibility issues.
        
        Args:
            html: HTML content to check
            
        Returns:
            List of accessibility issues
        """
        issues = []
        
        # Run enabled checks
        if self.config.check_alt_text:
            issues.extend(check_alt_text(html))
        
        if self.config.check_form_labels:
            issues.extend(check_form_labels(html))
        
        if self.config.check_heading_hierarchy:
            issues.extend(check_heading_hierarchy(html))
        
        if self.config.check_link_text:
            issues.extend(check_link_text(html))
        
        if self.config.check_aria_attributes:
            issues.extend(check_aria_attributes(html))
        
        # Filter issues based on WCAG level
        if self.config.wcag_level in ['A', 'AA', 'AAA']:
            filtered_issues = []
            for issue in issues:
                if not issue.wcag_criterion:
                    # Include issues without a specific criterion
                    filtered_issues.append(issue)
                    continue
                
                criterion = WCAG_GUIDELINES.get(issue.wcag_criterion, {})
                criterion_level = criterion.get('level', 'A')
                
                # Include issues based on configured level
                if self.config.wcag_level == 'A' and criterion_level == 'A':
                    filtered_issues.append(issue)
                elif self.config.wcag_level == 'AA' and criterion_level in ['A', 'AA']:
                    filtered_issues.append(issue)
                elif self.config.wcag_level == 'AAA':
                    filtered_issues.append(issue)
            
            issues = filtered_issues
        
        return issues
    
    def generate_report(self, issues: List[AccessibilityIssue], url: Optional[str] = None) -> Dict[str, Any]:
        """Generate accessibility report.
        
        Args:
            issues: List of accessibility issues
            url: URL that was checked
            
        Returns:
            Report as dictionary
        """
        # Count issues by severity
        severity_counts = {
            'error': 0,
            'warning': 0,
            'info': 0
        }
        
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        # Count issues by WCAG criterion
        criterion_counts = {}
        for issue in issues:
            if issue.wcag_criterion:
                criterion_counts[issue.wcag_criterion] = criterion_counts.get(issue.wcag_criterion, 0) + 1
        
        # Generate report
        report = {
            'url': url,
            'timestamp': datetime.utcnow().isoformat(),
            'wcag_level': self.config.wcag_level,
            'total_issues': len(issues),
            'severity_counts': severity_counts,
            'criterion_counts': criterion_counts,
            'issues': [issue.to_dict() for issue in issues]
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save accessibility report to file.
        
        Args:
            report: Report data
            filename: Optional filename
            
        Returns:
            Path to saved report
        """
        if not filename:
            timestamp = report.get('timestamp', '').replace(':', '-').replace('.', '-')
            url_part = ''
            if report.get('url'):
                url_part = re.sub(r'[^\w\-]', '_', report['url'])
                url_part = url_part[:50]  # Limit length
            
            filename = f"accessibility_report_{url_part}_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(self.config.report_path, exist_ok=True)
        
        # Save report
        report_path = os.path.join(self.config.report_path, filename)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_path

# Initialize with default configuration
# Note: This checker instance can be imported and used by FastAPI middleware.
accessibility_checker = AccessibilityChecker()