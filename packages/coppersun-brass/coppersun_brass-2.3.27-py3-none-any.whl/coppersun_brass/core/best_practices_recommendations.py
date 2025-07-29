"""
Best Practices Recommendations Engine for Copper Sun Brass

Modern implementation that provides actionable best practices recommendations
based on project analysis. Directly integrated with OutputGenerator.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class BestPracticesRecommendationEngine:
    """Generates actionable best practices recommendations based on project analysis."""
    
    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the Best Practices Recommendation Engine.
        
        Args:
            project_path: Root path of the project to analyze
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        
        # Define recommendation templates with modern best practices
        self.recommendation_templates = {
            'security_scanning': {
                'title': 'Implement Automated Security Scanning',
                'description': 'Add automated security vulnerability scanning to your CI/CD pipeline',
                'implementation': 'Use tools like Snyk, GitHub Security Scanning, or OWASP Dependency Check',
                'rationale': 'Identifies vulnerabilities early in development cycle, reducing security debt',
                'references': ['OWASP DevSecOps Guideline', 'NIST 800-53 SA-11'],
                'priority': 90,
                'category': 'security'
            },
            'input_validation': {
                'title': 'Comprehensive Input Validation',
                'description': 'Implement strict input validation for all user-provided data',
                'implementation': 'Use schema validation libraries (Joi, Yup, Pydantic) and sanitize all inputs',
                'rationale': 'Prevents injection attacks and data corruption issues',
                'references': ['OWASP Input Validation Cheat Sheet', 'CWE-20'],
                'priority': 85,
                'category': 'security'
            },
            'error_handling': {
                'title': 'Structured Error Handling and Logging',
                'description': 'Implement comprehensive error handling with structured logging',
                'implementation': 'Use structured logging libraries with correlation IDs and error context',
                'rationale': 'Essential for debugging production issues and security incident response',
                'references': ['OWASP Logging Cheat Sheet', 'NIST 800-92'],
                'priority': 80,
                'category': 'reliability'
            },
            'code_review': {
                'title': 'Mandatory Code Review Process',
                'description': 'Establish mandatory peer code review for all changes',
                'implementation': 'Use pull request workflows with required approvals and automated checks',
                'rationale': 'Catches bugs early, shares knowledge, and improves code quality',
                'references': ['IEEE 1028-2008', 'Google Engineering Practices'],
                'priority': 85,
                'category': 'quality'
            },
            'test_coverage': {
                'title': 'Comprehensive Test Coverage',
                'description': 'Achieve and maintain at least 80% code coverage with quality tests',
                'implementation': 'Use coverage tools, focus on critical paths and edge cases',
                'rationale': 'Reduces regression bugs and enables confident refactoring',
                'references': ['Martin Fowler Test Coverage', 'IEEE 829-2008'],
                'priority': 75,
                'category': 'quality'
            },
            'documentation': {
                'title': 'Comprehensive Documentation',
                'description': 'Maintain up-to-date documentation for architecture, APIs, and deployment',
                'implementation': 'Use tools like Swagger/OpenAPI, architecture decision records (ADRs)',
                'rationale': 'Reduces onboarding time and prevents knowledge silos',
                'references': ['RFC 2119', 'ISO/IEC/IEEE 26515:2018'],
                'priority': 70,
                'category': 'maintainability'
            },
            'dependency_management': {
                'title': 'Automated Dependency Management',
                'description': 'Implement automated dependency updates with security scanning',
                'implementation': 'Use Dependabot, Renovate, or similar tools with automated testing',
                'rationale': 'Prevents security vulnerabilities from outdated dependencies',
                'references': ['OWASP A06:2021', 'NIST 800-161'],
                'priority': 75,
                'category': 'security'
            },
            'monitoring': {
                'title': 'Production Monitoring and Alerting',
                'description': 'Implement comprehensive monitoring with proactive alerting',
                'implementation': 'Use APM tools (DataDog, New Relic) with custom metrics and alerts',
                'rationale': 'Enables rapid incident response and performance optimization',
                'references': ['SRE Book Ch. 6', 'NIST 800-137'],
                'priority': 80,
                'category': 'operations'
            },
            'api_versioning': {
                'title': 'API Versioning Strategy',
                'description': 'Implement clear API versioning for backward compatibility',
                'implementation': 'Use semantic versioning with deprecation policies',
                'rationale': 'Prevents breaking changes for API consumers',
                'references': ['REST API Design Rulebook', 'RFC 7231'],
                'priority': 70,
                'category': 'architecture'
            },
            'secrets_management': {
                'title': 'Secure Secrets Management',
                'description': 'Never commit secrets; use secure secret management solutions',
                'implementation': 'Use HashiCorp Vault, AWS Secrets Manager, or environment variables',
                'rationale': 'Prevents credential exposure and security breaches',
                'references': ['OWASP A07:2021', 'NIST 800-57'],
                'priority': 95,
                'category': 'security'
            },
            
            # AI Coding Best Practices
            'ai_structured_planning': {
                'title': 'AI-Assisted Structured Planning',
                'description': 'Use structured planning with AI before implementation',
                'implementation': 'Ask AI to analyze requirements and create implementation plans before coding',
                'rationale': 'Improves code quality and reduces implementation errors',
                'references': ['Anthropic Claude Code Best Practices', 'AI Coding Workflow Standards'],
                'priority': 80,
                'category': 'ai_workflow'
            },
            'ai_context_loading': {
                'title': 'AI Context Loading Strategy',
                'description': 'Load project context systematically before asking AI for code changes',
                'implementation': 'Read relevant files first, then ask for analysis before requesting code generation',
                'rationale': 'Provides AI with necessary context for better code generation',
                'references': ['AI Prompt Engineering Best Practices', 'Claude Code Documentation'],
                'priority': 75,
                'category': 'ai_workflow'
            },
            'ai_iterative_refinement': {
                'title': 'AI Iterative Refinement Process',
                'description': 'Break complex coding tasks into smaller, manageable AI prompts',
                'implementation': 'Use step-by-step approach with feedback loops and incremental improvements',
                'rationale': 'Prevents AI from generating overly complex or incorrect solutions',
                'references': ['Prompt Engineering Standards', 'AI Development Workflows'],
                'priority': 70,
                'category': 'ai_workflow'
            },
            'ai_code_testing': {
                'title': 'Mandatory AI Code Testing',
                'description': 'Always test, lint, and type-check AI-generated code',
                'implementation': 'Run automated tests, linting tools, and type checking after AI code generation',
                'rationale': 'AI can introduce bugs, security vulnerabilities, and style inconsistencies',
                'references': ['AI Code Quality Standards', 'Automated Testing Best Practices'],
                'priority': 90,
                'category': 'ai_quality'
            },
            'ai_security_review': {
                'title': 'AI Code Security Review',
                'description': 'Conduct manual security review of all AI-generated code',
                'implementation': 'Review AI output for common vulnerabilities, injection attacks, and security flaws',
                'rationale': 'AI models can inadvertently introduce security vulnerabilities',
                'references': ['OWASP AI Security Guidelines', 'Secure AI Coding Practices'],
                'priority': 85,
                'category': 'ai_security'
            },
            'ai_prompt_engineering': {
                'title': 'Structured AI Prompt Engineering',
                'description': 'Use clear, specific prompts with examples and context',
                'implementation': 'Include requirements, constraints, examples, and expected output format in prompts',
                'rationale': 'Better prompts lead to higher quality, more relevant AI-generated code',
                'references': ['Prompt Engineering Guide', 'AI Communication Standards'],
                'priority': 75,
                'category': 'ai_quality'
            },
            'ai_version_control': {
                'title': 'AI Change Tracking',
                'description': 'Track and document AI-generated code modifications separately',
                'implementation': 'Use commit messages and documentation to identify AI-generated changes',
                'rationale': 'Enables better debugging and maintenance of AI-assisted codebases',
                'references': ['Version Control Best Practices', 'AI Development Documentation'],
                'priority': 65,
                'category': 'ai_workflow'
            },
            'ai_human_oversight': {
                'title': 'Mandatory Human Oversight',
                'description': 'Maintain human oversight and decision-making in AI-assisted development',
                'implementation': 'Use AI as an assistant, not a replacement for human judgment and expertise',
                'rationale': 'AI lacks context awareness and can make inappropriate architectural decisions',
                'references': ['AI Ethics in Software Development', 'Human-AI Collaboration Standards'],
                'priority': 95,
                'category': 'ai_safety'
            },
            'ai_fallback_strategies': {
                'title': 'AI Failure Fallback Strategies',
                'description': 'Maintain manual development approaches when AI assistance fails',
                'implementation': 'Have documented procedures for continuing development without AI assistance',
                'rationale': 'Ensures project continuity when AI tools are unavailable or ineffective',
                'references': ['Development Continuity Planning', 'AI Reliability Considerations'],
                'priority': 70,
                'category': 'ai_safety'
            }
        }

    def analyze_project(self, 
                       security_issues: List[Dict[str, Any]] = None,
                       todos: List[Dict[str, Any]] = None,
                       code_entities: List[Dict[str, Any]] = None,
                       code_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze project characteristics to determine relevant recommendations.
        
        Args:
            security_issues: List of security issues found
            todos: List of TODO items in code
            code_entities: List of code entities (functions, classes)
            code_metrics: Overall code metrics
            
        Returns:
            Analysis results with project characteristics
        """
        analysis = {
            'project_size': 'unknown',
            'languages': set(),
            'frameworks': set(),
            'has_tests': False,
            'has_ci': False,
            'has_docs': False,
            'security_score': 100,  # Start at 100, deduct for issues
            'quality_score': 100,
            'identified_gaps': []
        }
        
        try:
            # Analyze file structure
            file_stats = self._analyze_file_structure()
            analysis['languages'] = file_stats['languages']
            analysis['project_size'] = file_stats['size']
            analysis['has_tests'] = file_stats['has_tests']
            analysis['has_docs'] = file_stats['has_docs']
            analysis['has_ci'] = file_stats['has_ci']
            
            # Analyze security posture
            if security_issues:
                critical_count = len([s for s in security_issues if s.get('severity') == 'critical'])
                high_count = len([s for s in security_issues if s.get('severity') == 'high'])
                analysis['security_score'] -= (critical_count * 20 + high_count * 10)
                analysis['security_score'] = max(0, analysis['security_score'])
                
                if critical_count > 0:
                    analysis['identified_gaps'].append('critical_security_issues')
                if high_count > 2:
                    analysis['identified_gaps'].append('multiple_security_issues')
            
            # Analyze code quality
            if code_metrics:
                avg_complexity = code_metrics.get('average_complexity', 0)
                doc_coverage = code_metrics.get('documentation_coverage', 0)
                
                if avg_complexity > 10:
                    analysis['quality_score'] -= 20
                    analysis['identified_gaps'].append('high_complexity')
                if doc_coverage < 0.3:
                    analysis['quality_score'] -= 15
                    analysis['identified_gaps'].append('low_documentation')
            
            # Analyze TODOs for patterns
            if todos:
                security_todos = len([t for t in todos if 'security' in str(t).lower() or 'auth' in str(t).lower()])
                if security_todos > 3:
                    analysis['identified_gaps'].append('security_debt')
            
            # Detect observable AI-related problems from project analysis
            ai_issues = self._detect_ai_related_issues(security_issues, todos, code_entities, code_metrics)
            analysis['identified_gaps'].extend(ai_issues)
            
            # Check for missing critical components
            if not analysis['has_tests']:
                analysis['identified_gaps'].append('missing_tests')
            if not analysis['has_ci']:
                analysis['identified_gaps'].append('missing_ci')
            
        except Exception as e:
            logger.warning(f"Error during project analysis: {e}")
        
        return analysis

    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze project file structure to identify characteristics."""
        stats = {
            'languages': set(),
            'size': 'small',
            'has_tests': False,
            'has_docs': False,
            'has_ci': False,
            'file_count': 0
        }
        
        try:
            # Count files by extension
            extension_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.jsx': 'React',
                '.tsx': 'React',
                '.java': 'Java',
                '.go': 'Go',
                '.rs': 'Rust',
                '.rb': 'Ruby',
                '.php': 'PHP',
                '.cs': 'C#',
                '.cpp': 'C++',
                '.c': 'C',
                '.swift': 'Swift',
                '.kt': 'Kotlin'
            }
            
            file_count = 0
            for ext, lang in extension_map.items():
                files = list(self.project_path.rglob(f'*{ext}'))
                if files:
                    stats['languages'].add(lang)
                    file_count += len(files)
            
            stats['file_count'] = file_count
            
            # Determine project size
            if file_count > 100:
                stats['size'] = 'large'
            elif file_count > 30:
                stats['size'] = 'medium'
            else:
                stats['size'] = 'small'
            
            # Check for test files
            test_patterns = ['test_*.py', '*.test.js', '*.spec.js', '*.test.ts', '*.spec.ts']
            for pattern in test_patterns:
                if list(self.project_path.rglob(pattern)):
                    stats['has_tests'] = True
                    break
            if (self.project_path / 'tests').exists() or (self.project_path / 'test').exists():
                stats['has_tests'] = True
            
            # Check for documentation
            doc_files = ['README.md', 'README.rst', 'README.txt', 'CONTRIBUTING.md', 'docs']
            for doc in doc_files:
                if (self.project_path / doc).exists():
                    stats['has_docs'] = True
                    break
            
            # Check for CI/CD
            ci_files = ['.github/workflows', '.gitlab-ci.yml', 'Jenkinsfile', '.circleci', '.travis.yml']
            for ci in ci_files:
                if (self.project_path / ci).exists():
                    stats['has_ci'] = True
                    break
                    
        except Exception as e:
            logger.warning(f"Error analyzing file structure: {e}")
        
        return stats

    def _detect_ai_related_issues(self,
                                 security_issues: List[Dict[str, Any]] = None,
                                 todos: List[Dict[str, Any]] = None,
                                 code_entities: List[Dict[str, Any]] = None,
                                 code_metrics: Dict[str, Any] = None) -> List[str]:
        """Detect observable AI-related problems in the project.
        
        Returns:
            List of identified AI-related gaps based on actual evidence
        """
        issues = []
        
        # Evidence: Look for AI-generated code without tests
        if self._has_untested_ai_generated_code(code_entities, code_metrics):
            issues.append('untested_ai_code')
        
        # Evidence: Look for suspiciously uniform/repetitive code patterns
        if self._has_ai_code_patterns(code_entities):
            issues.append('ai_generated_code_quality')
        
        # Evidence: Look for TODOs mentioning AI tools or generated code
        if self._has_ai_related_todos(todos):
            issues.append('ai_workflow_debt')
        
        # Evidence: Look for security issues that commonly appear in AI-generated code
        if self._has_ai_typical_security_issues(security_issues):
            issues.append('ai_security_risks')
        
        # Evidence: Look for large functions that might need AI-assisted refactoring
        if self._has_complex_functions_needing_ai_help(code_entities):
            issues.append('complex_code_needs_ai_assistance')
        
        return issues
    
    def _has_untested_ai_generated_code(self, code_entities: List[Dict] = None, code_metrics: Dict = None) -> bool:
        """Check if there are signs of untested AI-generated code."""
        if not code_entities or not code_metrics:
            return False
        
        # Evidence: Very low test coverage + presence of repetitive function names
        test_coverage = code_metrics.get('documentation_coverage', 1.0)  # Using doc coverage as proxy
        
        if test_coverage < 0.1:  # Very low coverage
            # Look for repetitive patterns that suggest AI generation
            function_names = [e.get('entity_name', '') for e in code_entities if e.get('entity_type') == 'function']
            if len(function_names) > 5:
                # Check for naming patterns like func1, func2, or very similar names
                similar_names = sum(1 for i, name in enumerate(function_names) 
                                  for other in function_names[i+1:] 
                                  if name and other and (name in other or other in name))
                if similar_names > 3:
                    return True
        
        return False
    
    def _has_ai_code_patterns(self, code_entities: List[Dict] = None) -> bool:
        """Check for patterns typical of AI-generated code."""
        if not code_entities:
            return False
        
        # Evidence: Multiple entities with identical complexity scores (AI tends to generate uniform code)
        complexity_scores = [e.get('complexity_score', 0) for e in code_entities if e.get('complexity_score')]
        if len(complexity_scores) > 5:
            # Check if too many functions have identical complexity
            from collections import Counter
            complexity_counts = Counter(complexity_scores)
            max_identical = max(complexity_counts.values()) if complexity_counts else 0
            if max_identical > len(complexity_scores) * 0.4:  # 40% have same complexity
                return True
        
        return False
    
    def _has_ai_related_todos(self, todos: List[Dict] = None) -> bool:
        """Check for TODOs that mention AI tools or workflow issues."""
        if not todos:
            return False
        
        ai_keywords = ['ai', 'claude', 'gpt', 'generated', 'copilot', 'assistant', 'llm', 'prompt']
        ai_todo_count = 0
        
        for todo in todos:
            content = str(todo.get('content', '')).lower()
            if any(keyword in content for keyword in ai_keywords):
                ai_todo_count += 1
        
        return ai_todo_count > 2  # Multiple AI-related TODOs suggest workflow issues
    
    def _has_ai_typical_security_issues(self, security_issues: List[Dict] = None) -> bool:
        """Check for security issues commonly found in AI-generated code."""
        if not security_issues:
            return False
        
        # AI commonly generates code with these issues
        ai_common_patterns = [
            'hardcoded', 'sql injection', 'xss', 'path traversal', 
            'insecure random', 'weak encryption', 'missing validation'
        ]
        
        ai_related_issues = 0
        for issue in security_issues:
            description = str(issue.get('description', '')).lower()
            if any(pattern in description for pattern in ai_common_patterns):
                ai_related_issues += 1
        
        return ai_related_issues > 3  # Multiple typical AI security issues
    
    def _has_complex_functions_needing_ai_help(self, code_entities: List[Dict] = None) -> bool:
        """Check for overly complex functions that could benefit from AI-assisted refactoring."""
        if not code_entities:
            return False
        
        complex_functions = [e for e in code_entities 
                           if e.get('entity_type') == 'function' 
                           and e.get('complexity_score', 0) > 15]
        
        return len(complex_functions) > 2  # Multiple highly complex functions

    def generate_recommendations(self,
                               analysis: Dict[str, Any],
                               limit: int = 6) -> List[Dict[str, Any]]:
        """Generate prioritized recommendations based on project analysis.
        
        Args:
            analysis: Project analysis results
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommendations with full details
        """
        recommendations = []
        selected_keys = set()
        
        # Priority 1: Critical security gaps
        if 'critical_security_issues' in analysis['identified_gaps']:
            if 'input_validation' not in selected_keys:
                recommendations.append(self.recommendation_templates['input_validation'])
                selected_keys.add('input_validation')
            if 'security_scanning' not in selected_keys:
                recommendations.append(self.recommendation_templates['security_scanning'])
                selected_keys.add('security_scanning')
        
        # Priority 2: Missing critical components
        if 'missing_tests' in analysis['identified_gaps'] and 'test_coverage' not in selected_keys:
            recommendations.append(self.recommendation_templates['test_coverage'])
            selected_keys.add('test_coverage')
        
        if 'missing_ci' in analysis['identified_gaps'] and 'code_review' not in selected_keys:
            recommendations.append(self.recommendation_templates['code_review'])
            selected_keys.add('code_review')
        
        # Priority 3: Quality issues
        if 'high_complexity' in analysis['identified_gaps'] or 'technical_debt' in analysis['identified_gaps']:
            if 'error_handling' not in selected_keys:
                recommendations.append(self.recommendation_templates['error_handling'])
                selected_keys.add('error_handling')
        
        if 'low_documentation' in analysis['identified_gaps'] and 'documentation' not in selected_keys:
            recommendations.append(self.recommendation_templates['documentation'])
            selected_keys.add('documentation')
        
        # Priority 4: General best practices based on project size
        if analysis['project_size'] in ['medium', 'large']:
            if 'monitoring' not in selected_keys and len(recommendations) < limit:
                recommendations.append(self.recommendation_templates['monitoring'])
                selected_keys.add('monitoring')
            if 'dependency_management' not in selected_keys and len(recommendations) < limit:
                recommendations.append(self.recommendation_templates['dependency_management'])
                selected_keys.add('dependency_management')
        
        # Priority 5: Evidence-based AI recommendations
        # Only recommend based on actual observed problems
        
        if 'untested_ai_code' in analysis['identified_gaps'] and 'ai_code_testing' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_code_testing'])
            selected_keys.add('ai_code_testing')
        
        if 'ai_security_risks' in analysis['identified_gaps'] and 'ai_security_review' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_security_review'])
            selected_keys.add('ai_security_review')
        
        if 'ai_workflow_debt' in analysis['identified_gaps'] and 'ai_structured_planning' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_structured_planning'])
            selected_keys.add('ai_structured_planning')
        
        if 'complex_code_needs_ai_assistance' in analysis['identified_gaps'] and 'ai_iterative_refinement' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_iterative_refinement'])
            selected_keys.add('ai_iterative_refinement')
        
        if 'ai_generated_code_quality' in analysis['identified_gaps'] and 'ai_prompt_engineering' not in selected_keys:
            recommendations.append(self.recommendation_templates['ai_prompt_engineering'])
            selected_keys.add('ai_prompt_engineering')
        
        # Always include secrets management if not already included
        if 'secrets_management' not in selected_keys and len(recommendations) < limit:
            recommendations.append(self.recommendation_templates['secrets_management'])
            selected_keys.add('secrets_management')
        
        # Fill remaining slots with other relevant recommendations
        remaining_keys = set(self.recommendation_templates.keys()) - selected_keys
        for key in sorted(remaining_keys, 
                         key=lambda k: self.recommendation_templates[k]['priority'], 
                         reverse=True):
            if len(recommendations) >= limit:
                break
            recommendations.append(self.recommendation_templates[key])
        
        # Sort by priority
        recommendations.sort(key=lambda r: r['priority'], reverse=True)
        
        return recommendations[:limit]

    def format_recommendations_for_output(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """Format recommendations for markdown output.
        
        Args:
            recommendations: List of recommendation dictionaries
            
        Returns:
            List of formatted markdown strings
        """
        formatted = []
        
        for rec in recommendations:
            # Determine icon based on priority
            if rec['priority'] >= 90:
                icon = "🚨"
            elif rec['priority'] >= 80:
                icon = "🔴"
            elif rec['priority'] >= 70:
                icon = "🟡"
            else:
                icon = "🟢"
            
            # Format the recommendation
            lines = [f"{icon} **{rec['title']}** (Priority: {rec['priority']})"]
            
            if rec.get('description'):
                lines.append(f"  - *Description*: {rec['description']}")
            
            if rec.get('implementation'):
                lines.append(f"  - *Implementation*: {rec['implementation']}")
            
            if rec.get('rationale'):
                lines.append(f"  - *Why*: {rec['rationale']}")
            
            if rec.get('references'):
                refs = ", ".join(rec['references'])
                lines.append(f"  - *References*: {refs}")
            
            formatted.append("\n".join(lines))
        
        return formatted