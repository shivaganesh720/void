import os
import re

replacements = {
    r'from app\.errors import': 'from app.core.exceptions import',
    r'import app\.errors': 'import app.core.exceptions as errors',
    r'from app\.contracts\.schemas import': 'from app.schemas import',
    r'from app\.contracts\.enums import': 'from app.models.enums import',
    r'from app\.db\.base import': 'from app.models.base import',
    r'from app\.api\.middleware import': 'from app.middleware import',
    r'from app\.control_plane\.policy import': 'from app.policies.evaluator import',
    r'from app\.governance\.admin import': 'from app.policies.permissions import',
    r'from app\.governance\.audit import': 'from app.policies.rules import',
    r'from app\.governance\.observability import': 'from app.utils.observability import',
    r'from app\.gateways\.model_gateway import': 'from app.integrations.providers import',
    r'from app\.gateways\.tool_gateway import': 'from app.integrations.base import',
    r'from app\.files\.validation import': 'from app.utils.files import',
    r'from app\.files\.parsing import': 'from app.utils.text import',
    r'from app\.workflows\.resume_jd import': 'from app.capabilities.resume_jd.service import',
    r'from app\.workflows\.resume_jd_analysis import': 'from app.capabilities.resume_jd.parser import',
    r'from app\.workflows\.engine import': 'from app.execution.runner import',
    r'from app\.control_plane\.engine import': 'from app.execution.lifecycle import',
    r'from app\.control_plane\.intent import': 'from app.execution.execution_control import',
    r'from app\.control_plane\.state import': 'from app.execution.task_state import',
    r'from app\.control_plane\.strategy import': 'from app.execution.scheduler import',
    r'from app\.control_plane\.capabilities import': 'from app.capabilities.registry import',
    r'from app\.execution\.agents import': 'from app.capabilities.broker import',
    r'from app\.execution\.graph import': 'from app.execution.mission_kernel import',
    r'from app\.execution\.manager import': 'from app.execution.recovery import',
    r'from app\.routers\.': 'from app.api.v1.',
}

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old, new in replacements.items():
                    content = re.sub(old, new, content)
                
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")

if __name__ == '__main__':
    process_directory('apps/backend/app')
    process_directory('apps/backend/tests')
    process_directory('apps/backend/scripts')
