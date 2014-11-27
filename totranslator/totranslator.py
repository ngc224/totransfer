#!/usr/bin/env python
# -*- coding:utf-8 -*-

from clint import textui
import sys, os, argparse, ConfigParser, requests, keyring, feedparser
import config as sys_config


class ToTranslator():
    def __init__(self):
        self.response = None

    def request(self, access_key, text, lang_to, lang_from):
        self.response = requests.post(
            sys_config.api_request_url,
            params={'Text': "'%s'" % text, 'To': "'%s'" % lang_to, 'From': "'%s'" % lang_from},
            auth=(access_key, access_key)
        )
        if not self.isStatusCode(self.response.status_code):
            raise
        return self

    def parse(self):
        for e in feedparser.parse(self.response.text)['entries']:
            return e['m_properties_detail']['value']

    @staticmethod
    def isStatusCode(code):
        return code == 200

    @staticmethod
    def isLang(lang):
        return lang in ToTranslator.getLangList()

    @staticmethod
    def getLangList():
        return ['ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en', 'es', 'et', 'fa', 'fi', 'fr', 'he', 'hi', 'ht', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ms', 'mww', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'ur', 'vi', 'zh-CHS', 'zh-CHT']


class UserConfig():
    def __init__(self, filepath):
        self.filepath = filepath
        self.user_config = ConfigParser.SafeConfigParser()
        try:
            if not os.path.isfile(self.filepath):
                raise IOError(self.filepath)
        except:
            user_config = ConfigParser.RawConfigParser()
            user_config.add_section(sys_config.application_name)
            user_config.set(sys_config.application_name, 'From', '')
            user_config.set(sys_config.application_name, 'To', '')
            with open(self.filepath, 'wb') as configfile:
                user_config.write(configfile)
                os.chmod(self.filepath, 0644)
        self.user_config.read(self.filepath)

    def getUserOption(self, option):
        if self.user_config.has_option(sys_config.application_name, option):
            return self.user_config.get(sys_config.application_name, option)

    def setAccessKey(self):
        print(textui.colored.green('Get Evernote developer token --> ' + sys_config.accesskey_get_url))
        keyring.set_password(sys_config.application_name, 'access_key', raw_input('Access key: '))
        return self

    @staticmethod
    def getAccessKey():
        return keyring.get_password(sys_config.application_name, 'access_key')

    def setDefaultFromLang(self):
        print(textui.colored.green('Set totranslator default post tags / Not enter if you do not set'))
        self.user_config.set(sys_config.application_name, 'From', raw_input('From lang: '))
        return self

    def setDefaultToLang(self):
        print(textui.colored.green('Set totranslator default post notebook / Not enter if you do not set'))
        self.user_config.set(sys_config.application_name, 'To', raw_input('To lang: '))
        return self

    def save(self):
        self.user_config.write(open(self.filepath, 'w'))








class Util():
    @staticmethod
    def isBinary(data):
        for encoding in ['utf-8', 'shift-jis', 'euc-jp', 'iso2022-jp']:
            try:
                data = data.decode(encoding)
                break
            except:
                pass
        if isinstance(data, unicode):
            return False
        return True


def main():
    parser = argparse.ArgumentParser(description=sys_config.application_name + ' version ' + sys_config.version)
    parser.add_argument('file', nargs='?', action='store', help='file to send to evernote')
    parser.add_argument('--from', type=str, help='note attachment file name')
    parser.add_argument('--to', type=str, help='note title (omitted, the time is inputted automatically.)')
    parser.add_argument('--config', action='store_true', help='set user config')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + sys_config.version)










    # aaa = ToTranslator().request('nIPCSzvQVju2gS1XemNy1FjGuIBxq903bN1YWeXd5jw', '埼玉県', 'en', 'ja').parse()
    #
    # print aaa
    #
    # sys.exit(0)












    args = parser.parse_args()
    user_config = UserConfig(sys_config.user_filepath)

    # Set config
    if args.config:
        try:
            user_config.setAccessKey().setDefaultFromLang().setDefaultFromLang().save()
        except:
            return 1
        return 0

    # File check
    if not args.file is None:
        if not os.path.isfile(args.file):
            print(textui.colored.red('File does not exist ' + args.file))
            return 1
        sys.stdin = open(args.file, 'r')
        if Util.isBinary(open(args.file, 'r').read()):
            return 1


    # Set lang to
    if not args.to and user_config.getUserOption('to'):
        args.to = user_config.getUserOption('to')
    if not ToTranslator().isLang(args.to):
        return 1














    # Set text stream
    try:
        for line in iter(sys.stdin.readline, ''):
            note_content += totranslator.getContentFormat(line)
            print(textui.colored.green(line.rstrip()))
    except:
        pass
    finally:
        # create note
        if totranslator.isSetContent(note_content):
            return totranslator.createNote(note_title, note_content, note_tags, note_bookguid)
    return 1


if __name__ == "__main__":
    sys.exit(main())
