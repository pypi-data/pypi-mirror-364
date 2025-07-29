import click
from .provider import (
    create_provider,
    list_providers,
    get_provider,
    update_provider,
    delete_provider,
)
from .endpoint import (
    create_endpoint,
    list_endpoints,
    get_endpoint,
    delete_endpoint,
)
from .version import (
    list_versions,
    get_model_version,
    get_version,
    delete_model_version,
    update_model_version,
    promote_version,
)
from .model import (
    create_model,
    update_model,
    list_models,
    get_model,
    delete_model,
    recover_model,
    list_model_types,
    list_model_tags,
    add_tags_to_model,
    remove_tags_from_model,
    add_languages_to_model,
    remove_languages_from_model,
    add_tasks_to_model,
    remove_tasks_from_model,
)
from .custom_runtime import (
    create_custom_runtime,
    get_custom_runtime_by_model,
    delete_custom_runtime_by_model,
)
from tabulate import tabulate
import json as json_module


def print_model_detail(model, title=None):
    """Prints a single model as a table."""
    if not model:
        click.secho("No model found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Field", "Value"]
    rows = []
    for key, value in model.items():
        # custom_runtime은 별도로 처리
        if key == 'custom_runtime' and isinstance(value, dict):
            # custom_runtime 정보를 모델 테이블 아래에 append
            rows.append(["custom_runtime_id", value.get('id', '-')])
            rows.append(["custom_runtime_image_url", value.get('image_url', '-')])
            rows.append(["custom_runtime_use_bash", value.get('use_bash', '-')])
            rows.append(["custom_runtime_command", ', '.join(value.get('command', [])) if value.get('command') else '-'])
            rows.append(["custom_runtime_args", ', '.join(value.get('args', [])) if value.get('args') else '-'])
            rows.append(["custom_runtime_created_at", value.get('created_at', '-')])
            rows.append(["custom_runtime_updated_at", value.get('updated_at', '-')])
            continue
        
        # languages, tasks, tags는 name만 추출해서 쉼표로 구분
        if key in ['languages', 'tasks', 'tags'] and hasattr(value, '__iter__') and not isinstance(value, str):
            names = [item.get('name', '') for item in value if isinstance(item, dict)]
            display_value = ', '.join(names) if names else '-'
        else:
            display_value = value
        rows.append([key, display_value])
    click.echo(tabulate(rows, headers, tablefmt="github"))

def print_model_list(models, title=None):
    """Prints a list of models as a table."""
    if not models:
        click.secho("No models found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "Name", "Display Name", "Type", "Serving Type", "Size", "Valid", "Custom", "Provider", "tag", "task", "Updated"]
    rows = []
    for m in models:
        # Name을 30자로 제한
        name = m.get("name", "")
        if len(name) > 30:
            name = name[:27] + "..."
        
        # Display Name 처리 (30자로 제한)
        display_name = m.get("display_name", "")
        if not display_name:
            display_name = "-"
        elif len(display_name) > 30:
            display_name = display_name[:27] + "..."
        
        # Size 정보 처리
        size = m.get("size", "")
        if size:
            # 크기를 읽기 쉽게 변환 (예: 7B, 70B 등)
            if size.endswith("000000000"):
                size = size[:-9] + "B"
            elif size.endswith("000000"):
                size = size[:-6] + "M"
        
        # Valid 상태
        is_valid = "✅" if m.get("is_valid", True) else "❌"
        
        # Custom 상태
        is_custom = "✅" if m.get("is_custom", False) else "-"
        
        # Provider ID를 짧게 표시
        provider_name = m.get("provider_name", "")
        
        # tags name만 추출
        tags = m.get("tags", [])
        if hasattr(tags, '__iter__') and not isinstance(tags, str):
            tag_names = ', '.join([t.get('name', '') for t in tags if isinstance(t, dict)])
        else:
            tag_names = '-'
        
        # tasks name만 추출
        tasks = m.get("tasks", [])
        if hasattr(tasks, '__iter__') and not isinstance(tasks, str):
            task_names = ', '.join([t.get('name', '') for t in tasks if isinstance(t, dict)])
        else:
            task_names = '-'
        
        # Created At을 간단하게 표시
        updated_at = m.get("updated_at", "")
        if updated_at:
            updated_at = updated_at.split("T")[0]  # YYYY-MM-DD만 표시
        
        rows.append([
            m.get("id", ""), 
            name, 
            display_name,
            m.get("type", ""), 
            m.get("serving_type", ""),
            size,
            is_valid,
            is_custom,
            provider_name, 
            tag_names,
            task_names,
            updated_at
        ])
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_endpoint_list(endpoints, title=None):
    if not endpoints:
        click.secho("No endpoints found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "URL", "Identifier", "Key", "Description"]
    rows = [
        [e.get("id"), e.get("url"), e.get("identifier"), e.get("key"), e.get("description")] for e in endpoints
    ]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_version_list(versions, title=None):
    if not versions:
        click.secho("No versions found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "Display Name", "Description", "Created"]
    rows = [
        [v.get("id"), v.get("display_name"), v.get("description"), v.get("created_at")] for v in versions
    ]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_type_list(types, title=None):
    if not types:
        click.secho("No model types found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Type"]
    rows = [[t] for t in types]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_tag_list(tags, title=None):
    if not tags:
        click.secho("No model tags found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["Tag"]
    rows = [[t] for t in tags]
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_provider_list(providers, title=None):
    if not providers:
        click.secho("No providers found.", fg="yellow")
        return
    if title:
        click.secho(title, fg="cyan")
    headers = ["ID", "Name", "Description", "Created"]
    rows = []
    for p in providers:
        # Description을 30자로 제한
        desc = p.get("description", "")
        if len(desc) > 30:
            desc = desc[:27] + "..."
        # Created At을 간단하게 표시
        created_at = p.get("created_at", "")
        if created_at:
            created_at = created_at.split("T")[0]  # YYYY-MM-DD만 표시
        
        rows.append([p.get("id"), p.get("name"), desc, created_at])
    
    tablefmt = "github" if len(headers) <= 8 and len(rows) <= 10 else "simple"
    click.echo(tabulate(rows, headers, tablefmt=tablefmt))

def print_provider_detail(provider, title=None):
    if not provider:
        click.secho("No provider data.", fg="yellow")
        return
    if title:
        click.secho(title, fg="green")
    rows = [[k, v] for k, v in provider.items()]
    click.echo(tabulate(rows, headers=["Field", "Value"], tablefmt="github"))

def print_model_and_endpoint(model, endpoint):
    """모델과 엔드포인트 결과를 prefix를 붙여 한 줄 테이블로 출력"""
    combined = {}
    for k, v in model.items():
        combined[f"model_{k}"] = v
    for k, v in endpoint.items():
        combined[f"endpoint_{k}"] = v
    headers = list(combined.keys())
    values = [combined[k] for k in headers]
    tablefmt = "github" if len(headers) <= 8 else "simple"
    click.echo(tabulate([values], headers, tablefmt=tablefmt))

@click.group()
def model():
    """Command-line interface for AIP model catalog."""
    pass

@model.group()
def version():
    """Manage model versions and deployments."""
    pass

@version.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated version IDs')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(model_id, page, size, sort, filter, search, ids, json):
    """List versions for a specific model."""
    result = list_versions(model_id, page, size, sort, filter, search, ids)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        versions = result.get("data", result)
        print_version_list(versions, title="🏗️ Version List:")

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, version_id, json):
    """Get a specific version of a model."""
    result = get_model_version(model_id, version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Detail:")

@version.command('get-by-version')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get_by_version(version_id, json):
    """Get a specific version by version_id only."""
    result = get_version(version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Detail:")

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, version_id, json):
    """Delete a specific version of a model."""
    result = delete_model_version(model_id, version_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Deleted:")

@version.command()
@click.argument('model_id')
@click.argument('version_id')
@click.option('--description', default=None, help='Description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def update(model_id, version_id, description, json):
    """Update a specific version of a model (only description can be updated)."""
    data = {}
    if description is not None:
        data['description'] = description
    result = update_model_version(model_id, version_id, data)
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Updated:")

@version.command()
@click.argument('version_id')
@click.option('--display-name', prompt=True, help='Display name')
@click.option('--description', default='', help='Description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def promote(version_id, display_name, description, json):
    """Promote a specific version to a model."""
    data = {'display_name': display_name, 'description': description}
    result = promote_version(version_id, data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏗️ Version Promoted:")

@model.command()
@click.option('--name', help='Model name (for parameter style)')
@click.option('--type', 'model_type', help='Model type (for parameter style)')
@click.option('--display-name', help='Display name for the model')
@click.option('--description', default='', help='Model description')
@click.option('--size', help='Model size')
@click.option('--token-size', help='Token size')
@click.option('--dtype', help='Data type')
@click.option('--serving-type', help='Serving type (e.g., serverless)')
@click.option('--is-private', is_flag=True, default=False, help='Whether the model is private')
@click.option('--license', help='License information')
@click.option('--readme', help='README content')
@click.option('--path', help='Model file path (required for self-hosting models)')
@click.option('--provider-id', help='Provider ID')
@click.option('--is-custom', is_flag=True, default=False, help='Whether the model is custom')
@click.option('--custom-code-path', help='Custom code path')
@click.option('--tags', multiple=True, help='Model tags')
@click.option('--languages', multiple=True, help='Model languages')
@click.option('--tasks', multiple=True, help='Model tasks')
@click.option('--inference-param', help='Inference parameters (JSON string)')
@click.option('--quantization', help='Quantization parameters (JSON string)')
@click.option('--default-params', help='Default parameters (JSON string)')
@click.option('--endpoint-url', help='Endpoint URL (for serverless)')
@click.option('--endpoint-identifier', help='Endpoint identifier (for serverless)')
@click.option('--endpoint-key', help='Endpoint key (for serverless)')
@click.option('--endpoint-description', help='Endpoint description (for serverless)')
@click.option('--custom-runtime-image-url', help='Custom runtime image URL (required if is_custom=True)')
@click.option('--custom-runtime-use-bash', is_flag=True, default=False, help='Whether to use bash for custom runtime (default: False)')
@click.option('--custom-runtime-command', help='Custom runtime command (comma-separated values)')
@click.option('--custom-runtime-args', help='Custom runtime arguments (comma-separated values)')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Model creation JSON file path (for dict style)')
def create(name, model_type, display_name, description, size, token_size, dtype, serving_type, 
           is_private, license, readme, path, provider_id,
           is_custom, custom_code_path, tags, languages, tasks,
           inference_param, quantization, default_params, endpoint_url, endpoint_identifier, endpoint_key, endpoint_description, 
           custom_runtime_image_url, custom_runtime_use_bash, custom_runtime_command, custom_runtime_args, json_path):
    """Create a new model. (JSON file or params style both supported, file path options are auto uploaded)
    This process is complicated, so please refer to the examples below.

    \b
    Supports two styles:
    1. Parameter style: --name "model" --type "self-hosting" --path "/path/to/file.bin"
    2. JSON file style: --json model_config.json

    Examples:

    \b
    # Serverless model with endpoint
    adxp-cli model create \
     --display-name "display name of your model" \
     --name "name of your model" \
     --type language \
     --description "description of your model" \
     --serving-type serverless \
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \
     --languages Korean \
     --languages English \
     --tasks completion \
     --tasks chat \
     --tags team1 \
     --tags team2 \
     --endpoint-url "https://api.sktaip.com/v1" \
     --endpoint-identifier "openai/gpt-3.5-turbo" \
     --endpoint-key "key-1234567890"

    \b
    # Self-hosting model
    adxp-cli model create \
     --display-name "display name of your model" \
     --name "name of your model" \
     --type language \
     --description "description of your model" \
     --serving-type self-hosting \
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \
     --languages Korean \
     --tasks completion \
     --tags tag \
     --path /path/to/your-model.zip

    \b
    # Self-hosting model (Model custom serving)
    adxp-cli model create \
     --display-name "display name of your model" \
     --name "name of your model" \
     --type language \
     --description "description of your model" \
     --serving-type self-hosting \
     --provider-id 3fa85f64-5717-4562-b3fc-2c963f66afa6 \
     --languages Korean \
     --tasks completion \
     --tags tag \
     --path /path/to/your-model.zip \
     --is-custom \
     --custom-code-path /path/to/your-code.zip \
     --custom-runtime-image-url "https://hub.docker.com/r/adxpai/adxp-custom-runtime" \
     --custom-runtime-use-bash \
     --custom-runtime-command "/bin/bash,-c" \
     --custom-runtime-args "uvicorn,main:app"
    """
    
    if json_path:
        # JSON file style
        with open(json_path, 'r') as f:
            data = json_module.load(f)
        # endpoint 관련 옵션은 serverless일 때만 data에 포함, 아닐 때는 완전히 제거
        if data.get('serving_type') != 'serverless':
            for k in ['endpoint_url', 'endpoint_identifier', 'endpoint_key', 'endpoint_description']:
                if k in data:
                    del data[k]
        try:
            result = create_model(data)
            if isinstance(result, dict) and "model" in result and "endpoint" in result:
                print_model_detail(result["model"], title="✅ Model created:")
                print_endpoint_list([result["endpoint"]], title="🔗 Endpoint created:")
            elif isinstance(result, dict) and "model" in result:
                print_model_detail(result["model"], title="✅ Model created:")
            else:
                print_model_detail(result, title="✅ Model created:")
        except ValueError as e:
            raise click.ClickException(str(e))
    elif name and model_type:
        # Parameter style
        data = {
            'name': name,
            'type': model_type,
            'description': description,
            'is_private': is_private,
            'is_custom': is_custom
        }
        
        # Validate that path is provided for self-hosting models
        if model_type == 'self-hosting' and not path:
            raise click.ClickException("--path is required for self-hosting models")
        
        # Optional fields
        if display_name:
            data['display_name'] = display_name
        if size:
            data['size'] = size
        if token_size:
            data['token_size'] = token_size
        if dtype:
            data['dtype'] = dtype
        if serving_type:
            data['serving_type'] = serving_type
        if license:
            data['license'] = license
        if readme:
            data['readme'] = readme
        if path:
            data['path'] = path
        if provider_id:
            data['provider_id'] = provider_id
        if custom_code_path:
            data['custom_code_path'] = custom_code_path
        # Endpoint 관련 옵션 추가
        if endpoint_url:
            data['endpoint_url'] = endpoint_url
        if endpoint_identifier:
            data['endpoint_identifier'] = endpoint_identifier
        if endpoint_key:
            data['endpoint_key'] = endpoint_key
        if endpoint_description:
            data['endpoint_description'] = endpoint_description
        
        # Parse JSON parameters
        if inference_param:
            try:
                data['inference_param'] = json_module.loads(inference_param)
            except json_module.JSONDecodeError:
                raise click.ClickException("--inference-param must be valid JSON")
        
        if quantization:
            try:
                data['quantization'] = json_module.loads(quantization)
            except json_module.JSONDecodeError:
                raise click.ClickException("--quantization must be valid JSON")
        
        if default_params:
            try:
                data['default_params'] = json_module.loads(default_params)
            except json_module.JSONDecodeError:
                raise click.ClickException("--default-params must be valid JSON")
        
        # List fields
        if tags:
            data['tags'] = [{'name': tag} for tag in tags]
        if languages:
            data['languages'] = [{'name': lang} for lang in languages]
        if tasks:
            data['tasks'] = [{'name': task} for task in tasks]
        
        # Custom runtime fields
        if custom_runtime_image_url:
            data['custom_runtime_image_url'] = custom_runtime_image_url
        if custom_runtime_use_bash is not None:
            data['custom_runtime_use_bash'] = custom_runtime_use_bash
        if custom_runtime_command:
            # 쉼표로 구분된 문자열을 리스트로 변환
            data['custom_runtime_command'] = [cmd.strip() for cmd in custom_runtime_command.split(',')]
        if custom_runtime_args:
            # 쉼표로 구분된 문자열을 리스트로 변환
            data['custom_runtime_args'] = [arg.strip() for arg in custom_runtime_args.split(',')]
        
        # endpoint 관련 옵션은 serverless일 때만 data에 포함, 아닐 때는 완전히 제거
        if serving_type == 'serverless':
            if endpoint_url:
                data['endpoint_url'] = endpoint_url
            if endpoint_identifier:
                data['endpoint_identifier'] = endpoint_identifier
            if endpoint_key:
                data['endpoint_key'] = endpoint_key
            if endpoint_description:
                data['endpoint_description'] = endpoint_description
        else:
            # 혹시라도 남아있을 수 있으니 완전히 제거
            for k in ['endpoint_url', 'endpoint_identifier', 'endpoint_key', 'endpoint_description']:
                if k in data:
                    del data[k]
        
        try:
            result = create_model(data)
            if isinstance(result, dict) and "model" in result and "endpoint" in result:
                print_model_detail(result["model"], title="✅ Model created:")
                print_endpoint_list([result["endpoint"]], title="🔗 Endpoint created:")
            elif isinstance(result, dict) and "model" in result:
                print_model_detail(result["model"], title="✅ Model created:")
            else:
                print_model_detail(result, title="✅ Model created:")
        except ValueError as e:
            raise click.ClickException(str(e))
    else:
        raise click.ClickException(
            "Invalid parameters. Use either:\n"
            "1. Parameter style: --name 'model' --type 'self-hosting' --path '/path/to/file.bin'\n"
            "2. JSON file style: --json model_config.json"
        )

@model.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--ids', default=None, help='Comma-separated model IDs')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, ids, json):
    """List all models."""
    result = list_models(page, size, sort, filter, search, ids)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        models = result.get("data", result)
        print_model_list(models, title="🤖 Model List:")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, json):
    """Get a model by ID."""
    result = get_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🤖 Model Detail:")
        
        # serverless 모델이면 endpoint 정보도 함께 보여주기
        if result.get('serving_type') == 'serverless':
            try:
                endpoints_result = list_endpoints(model_id, page=1, size=10)
                if endpoints_result and endpoints_result.get('data'):
                    print_endpoint_list(endpoints_result['data'], title="🔗 Model Endpoints:")
            except Exception as e:
                click.secho(f"⚠️ Failed to get endpoints: {e}", fg="yellow")
        
        # self-hosting 모델이면 custom_runtime 정보도 함께 보여주기
        elif result.get('serving_type') == 'self-hosting' and result.get('is_custom'):
            try:
                custom_runtime = get_custom_runtime_by_model(model_id)
                if custom_runtime:
                    print_model_detail(custom_runtime, title="⚙️ Custom Runtime:")
            except Exception as e:
                click.secho(f"⚠️ Failed to get custom runtime: {e}", fg="yellow")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, json):
    """Delete a model by ID."""
    result = delete_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🗑️ Model Deleted:")

@model.command()
@click.argument('model_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def recover(model_id, json):
    """Recover a deleted model by ID."""
    result = recover_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="♻️ Model Recovered:")

@model.command()
@click.argument('model_id')
@click.option('--name', help='Model name')
@click.option('--type', 'model_type', help='Model type')
@click.option('--display-name', help='Display name for the model')
@click.option('--description', help='Model description')
@click.option('--size', help='Model size')
@click.option('--token-size', help='Token size')
@click.option('--dtype', help='Data type')
@click.option('--serving-type', help='Serving type (e.g., serverless)')
@click.option('--license', help='License information')
@click.option('--readme', help='README content')
@click.option('--provider-id', help='Provider ID')
@click.option('--inference-param', help='Inference parameters (JSON string)')
@click.option('--quantization', help='Quantization parameters (JSON string)')
@click.option('--default-params', help='Default parameters (JSON string)')
@click.option('--json', 'json_path', type=click.Path(exists=True), help='Model update JSON file path (alternative to individual options)')
@click.option('--json-output', is_flag=True, help='Output in JSON format')
def update(model_id, name, model_type, display_name, description, size, token_size, dtype, serving_type,
           license, readme, provider_id,
           inference_param, quantization, default_params, json_path, json_output):
    """Update a model using individual options or JSON file."""
    data = {}
    
    # If JSON file is provided, use it
    if json_path:
        import json
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        # Build data from individual options
        if name is not None:
            data['name'] = name
        if model_type is not None:
            data['type'] = model_type
        if display_name is not None:
            data['display_name'] = display_name
        if description is not None:
            data['description'] = description
        if size is not None:
            data['size'] = size
        if token_size is not None:
            data['token_size'] = token_size
        if dtype is not None:
            data['dtype'] = dtype
        if serving_type is not None:
            data['serving_type'] = serving_type
        if license is not None:
            data['license'] = license
        if readme is not None:
            data['readme'] = readme
        if provider_id is not None:
            data['provider_id'] = provider_id
        if inference_param is not None:
            try:
                data['inference_param'] = json.loads(inference_param)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for inference_param")
        if quantization is not None:
            try:
                data['quantization'] = json.loads(quantization)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for quantization")
        if default_params is not None:
            try:
                data['default_params'] = json.loads(default_params)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON format for default_params")
    
    if not data:
        raise click.ClickException("No update data provided. Use individual options or --json file.")
    
    result = update_model(model_id, data)
    
    if json_output:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="✅ Model Updated:")

@model.command('type-list')
@click.option('--json', is_flag=True, help='Output in JSON format')
def type_list(json):
    """List all model types."""
    types = list_model_types()
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(types, indent=2))
    else:
        print_type_list(types, title="📦 Model Types:")

@model.command('tag-list')
@click.option('--json', is_flag=True, help='Output in JSON format')
def tag_list(json):
    """List all model tags."""
    tags = list_model_tags()
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(tags, indent=2))
    else:
        print_tag_list(tags, title="🏷️ Model Tags:")

@model.command('tag-add')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def tag_add(model_id, tags, json):
    """Add tags to a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    result = add_tags_to_model(model_id, tag_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🏷️ Tags Added:")

@model.command('tag-remove')
@click.argument('model_id')
@click.argument('tags', nargs=-1)
def tag_remove(model_id, tags):
    """Remove tags from a specific model."""
    tag_list = [{'name': tag} for tag in tags]
    result = remove_tags_from_model(model_id, tag_list)
    print_model_detail(result, title="🏷️ Tags Removed:")

@model.command('lang-add')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def lang_add(model_id, languages, json):
    """Add languages to a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    result = add_languages_to_model(model_id, lang_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🌐 Languages Added:")

@model.command('lang-remove')
@click.argument('model_id')
@click.argument('languages', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def lang_remove(model_id, languages, json):
    """Remove languages from a specific model."""
    lang_list = [{'name': lang} for lang in languages]
    result = remove_languages_from_model(model_id, lang_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🌐 Languages Removed:")

@model.command('task-add')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def task_add(model_id, tasks, json):
    """Add tasks to a specific model."""
    task_list = [{'name': task} for task in tasks]
    result = add_tasks_to_model(model_id, task_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🛠️ Tasks Added:")

@model.command('task-remove')
@click.argument('model_id')
@click.argument('tasks', nargs=-1)
@click.option('--json', is_flag=True, help='Output in JSON format')
def task_remove(model_id, tasks, json):
    """Remove tasks from a specific model."""
    task_list = [{'name': task} for task in tasks]
    result = remove_tasks_from_model(model_id, task_list)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🛠️ Tasks Removed:")

# provider group 및 하위 명령어
@model.group()
def provider():
    """Manage model providers (SKT, OpenAI, Huggingface,etc.)."""
    pass

@provider.command()
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(page, size, sort, filter, search, json):
    """List model providers."""
    result = list_providers(page, size, sort, filter, search)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        providers = result.get("data", result)
        print_provider_list(providers, title="🏢 Provider List:")

@provider.command()
@click.argument('provider_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(provider_id, json):
    """Get a specific model provider."""
    result = get_provider(provider_id)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Detail:")

@provider.command()
@click.option('--name', prompt=True, required=True, help='Provider name. Provider name should be unique.')
@click.option('--logo', default='', help='Provider logo')
@click.option('--description', default='', help='Provider description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(name, logo, description, json):
    """Create a model provider."""
    data = {'name': name, 'logo': logo, 'description': description}
    result = create_provider(data)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Created:")

@provider.command()
@click.argument('provider_id')
@click.option('--name', default=None, help='Provider name')
@click.option('--logo', default=None, help='Provider logo')
@click.option('--description', default=None, help='Provider description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def update(provider_id, name, logo, description, json):
    """Update a specific model provider."""
    data = {}
    if name is not None:
        data['name'] = name
    if logo is not None:
        data['logo'] = logo
    if description is not None:
        data['description'] = description
    result = update_provider(provider_id, data)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Updated:")

@provider.command()
@click.argument('provider_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(provider_id, json):
    """Delete a specific model provider."""
    result = delete_provider(provider_id)
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_provider_detail(result, title="🏢 Provider Deleted:")

# endpoint group 및 하위 명령어를 provider group 바로 아래로 이동
@model.group()
def endpoint():
    """Manage model endpoints and API configurations."""
    pass

@endpoint.command()
@click.argument('model_id')
@click.option('--url', prompt=True, help='Endpoint URL')
@click.option('--identifier', prompt=True, help='Endpoint identifier')
@click.option('--key', prompt=True, help='Endpoint key')
@click.option('--description', default='', help='Endpoint description')
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(model_id, url, identifier, key, description, json):
    """Create a model endpoint."""
    data = {'url': url, 'identifier': identifier, 'key': key, 'description': description}
    result = create_endpoint(model_id, data)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Created:")

@endpoint.command()
@click.argument('model_id')
@click.option('--page', default=1, help='Page number')
@click.option('--size', default=10, help='Page size')
@click.option('--sort', default=None, help='Sort by')
@click.option('--filter', default=None, help='Filter')
@click.option('--search', default=None, help='Search keyword')
@click.option('--json', is_flag=True, help='Output in JSON format')
def list(model_id, page, size, sort, filter, search, json):
    """List model endpoints for a specific model."""
    result = list_endpoints(model_id, page, size, sort, filter, search)
    
    if json:
        import json as json_module
        click.echo(json_module.dumps(result, indent=2))
    else:
        endpoints = result.get("data", result)
        print_endpoint_list(endpoints, title="🔗 Endpoint List:")

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, endpoint_id, json):
    """Get a specific model endpoint."""
    result = get_endpoint(model_id, endpoint_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Detail:")

@endpoint.command()
@click.argument('model_id')
@click.argument('endpoint_id')
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, endpoint_id, json):
    """Delete a specific model endpoint."""
    result = delete_endpoint(model_id, endpoint_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🔗 Endpoint Deleted:")

# 19. custom-runtime group 및 하위 명령어
@model.group('custom-runtime')
def custom_runtime():
    """Manage custom runtime configurations for models."""
    pass

@custom_runtime.command("create")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option("--image-url", required=True, help="Custom Docker image URL")
@click.option("--use-bash", is_flag=True, default=False, help="Use Bash")
@click.option("--command", help="Execution command (comma-separated values)")
@click.option("--args", help="Execution arguments (comma-separated values)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def create(model_id, image_url, use_bash, command, args, json):
    """Create a custom runtime."""
    runtime_data = {
        "model_id": model_id,
        "image_url": image_url,
        "use_bash": use_bash,
        "command": [cmd.strip() for cmd in command.split(',')] if command else None,
        "args": [arg.strip() for arg in args.split(',')] if args else None
    }
    result = create_custom_runtime(runtime_data)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🧩 Custom Runtime Created:")

@custom_runtime.command("get")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def get(model_id, json):
    """Get a custom runtime."""
    result = get_custom_runtime_by_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        print_model_detail(result, title="🧩 Custom Runtime Detail:")

@custom_runtime.command("delete")
@click.option("--model-id", required=True, help="Model ID (UUID)")
@click.option('--json', is_flag=True, help='Output in JSON format')
def delete(model_id, json):
    """Delete a custom runtime."""
    result = delete_custom_runtime_by_model(model_id)
    
    if json:
        click.echo(json_module.dumps(result, indent=2))
    else:
        # 삭제 성공 메시지는 이미 delete_custom_runtime_by_model에서 출력됨
        if result:
            print_model_detail(result, title="🧩 Custom Runtime Deleted:")
        else:
            click.secho("🧩 Custom Runtime Deleted Successfully", fg="green")

@click.group()
def cli():
    """AIP Model CLI"""
    pass

cli.add_command(model)

if __name__ == "__main__":
    cli()