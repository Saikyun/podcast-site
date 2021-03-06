import subprocess
import os
import click
import sys
sys.path.append('..')
from episode_parser import extract_meta_data


@click.command()
@click.option('--template_path', prompt='Path to the After Effects project')
@click.option('--episode', prompt='Episode number')
@click.option('--use_open_project', help='Run script from the open project', default=0)
@click.option('--background', help='name of bakground file', default=None)
@click.option('--audio', help='name of audio file', default=None)
@click.option('--text', help='name of text file', default=None)
@click.option('--output', help='name of the rendered file', default=None)
@click.option('--render', help='should we auto-render', default=1)
def run_after_effects_script(template_path, episode, use_open_project, text, audio, background, output, render):
    name, occupation, company, subtitle = extract_meta_data(episode)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_name = "automate.jsx"
    script_path = os.path.join(dir_path, script_name)
    assets_path = os.path.join(dir_path, "assets")

    if text is None:
        text = "{}.txt".format(episode)
    if audio is None:
        audio = "{}.mp3".format(episode)
    if background is None:
        background= "{}.jpg".format(episode)
    if output is None:
        output = episode
    first_subtitle = company
    second_subtitle = occupation
    if subtitle is not None:
        first_subtitle = subtitle
    if  second_subtitle is None:
        second_subtitle = company

    args = [name, first_subtitle, second_subtitle, episode,text, audio,background,output, assets_path + "/", template_path, use_open_project, render]
    arg_string = ""
    for arg in args:
        arg_string += "'{}',".format(arg)
    arg_string = arg_string[:-1]

    function_call="render({})".format(arg_string)
    cmd = 'arch -x86_64 osascript ASfile.scpt "{}" "{}"'.format(script_path, function_call)
    print(cmd)
    ae = subprocess.call(cmd,shell=True)


if __name__ == '__main__':
    run_after_effects_script()
