import json
import tomli


def create_steps(steps: dict[dict]) -> dict[list]:
    enabled_steps: list[str] = get_active_steps(steps)
    group_files: dict[list] = get_available_steps_groups(steps)

    for step in enabled_steps:
        step_setting: str = 'default'
        step_group: int = 0
        script_name: str = steps.get(step).get('script_name')

        if 'step_setting' in steps.get(step):
            step_setting = steps.get(step).get('step_setting')

        configs_step: str = get_step_settings(steps, step_setting=step_setting)
        if 'step_group' in steps.get(step):
            step_group: int = int(steps.get(step).get('step_group'))

        directory_name: str = steps.get(step).get('directory_name')
        group_files[step_group].append(
            json.loads(configs_step % (directory_name, script_name, script_name))
        )
    return group_files


def sorts_steps(steps: list[str]) -> list[str]:
    return sorted(steps)


def get_step_settings(steps: list[str], step_setting: str) -> str:
    if step_setting in steps.get('step_settings'):
        return steps.get('step_settings').get(step_setting)
    return steps.get('step_settings').get('default')


def get_active_steps(steps: dict[dict]) -> list[str]:
    enabled_steps: list[str] = []
    for step in steps:
        if 'group_name' in steps[step]:
            group_name: str = steps[step].get('group_name')
            steps[step].update(get_group_config(steps, group_name))
        if steps[step].get('enabled'):
            enabled_steps.append(step)
    return sorts_steps(enabled_steps)


def get_group_config(steps: dict[dict], group_name: str) -> dict:
    group_config = steps.get('groups').get(group_name)
    if 'group_name' in group_config:
        group_config.update(get_group_config(steps, group_config.get('group_name')))
    return group_config


def get_available_steps_groups(steps: dict[dict]) -> dict[list]:
    available_groups: list[str] = []
    group_files: dict[list] = {}

    for step in steps:
        if 'step_group' in steps[step]:
            available_groups.append(int(steps[step].get('step_group')))
        else:
            available_groups.append(0)

    for g in set(available_groups):
        group_files[g] = []
    return group_files


def create_json_file(group: str, steps: list[dict], parallelism: bool = False) -> None:
    
    if len(steps):
        if parallelism:
            if group < 10:
                file_name = f'steps/00{group}_step_group.json'
            elif group < 100:
                file_name = f'steps/0{group}_step_group.json'
            else:
                file_name = f'steps/{group}_step_group.json'
        else:
            file_name = 'steps/steps.json'

        with open(file_name, 'w') as f:
            json.dump(steps, f, indent=4)


def main(steps_file_path: str = "conf/steps.toml"):
    with open(steps_file_path, "rb") as f:
        steps: dict = tomli.load(f)

    parallelism = steps.get('step_settings').get('parallelism')
    steps_files = create_steps(steps=steps)
    for group in sorted(steps_files.keys()):
        create_json_file(
            group=group,
            steps=steps_files.get(group),
            parallelism=parallelism
        )


if __name__ == '__main__':
    main()
