# -*- coding: utf-8 -*-
# Python 3
import hashlib, sys, re, platform, os

import pyaes
from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlparse
from html.entities import name2codepoint


class cParser:
    @staticmethod
    def parseSingleResult(sHtmlContent, pattern):
        aMatches = None
        if sHtmlContent:
            aMatches = re.findall(pattern, sHtmlContent, flags=re.S | re.M)
            if len(aMatches) == 1:
                aMatches[0] = cParser.replaceSpecialCharacters(aMatches[0])
                return True, aMatches[0]
        return False, aMatches

    @staticmethod
    def replaceSpecialCharacters(s):
        # Umlaute Unicode konvertieren
        for t in (('\\/', '/'), ('&amp;', '&'), ('\\u00c4', 'ÃƒÆ’Ã‚â€ž'), ('\\u00e4', 'ÃƒÆ’Ã‚Â¤'),
            ('\\u00d6', 'ÃƒÆ’Ã‚â€“'), ('\\u00f6', 'ÃƒÆ’Ã‚Â¶'), ('\\u00dc', 'ÃƒÆ’Ã‚Å“'), ('\\u00fc', 'ÃƒÆ’Ã‚Â¼'),
            ('\\u00df', 'ÃƒÆ’Ã‚Å¸'), ('\\u2013', '-'), ('\\u00b2', 'Ãƒâ€šÃ‚Â²'), ('\\u00b3', 'Ãƒâ€šÃ‚Â³'),
            ('\\u00e9', 'ÃƒÆ’Ã‚Â©'), ('\\u2018', 'ÃƒÂ¢Ã‚â‚¬Ã‚Ëœ'), ('\\u201e', 'ÃƒÂ¢Ã‚â‚¬Ã‚Å¾'), ('\\u201c', 'ÃƒÂ¢Ã‚â‚¬Ã‚Å“'),
            ('\\u00c9', 'ÃƒÆ’Ã‚â€°'), ('\\u2026', '...'), ('\\u202fh', 'h'), ('\\u2019', 'ÃƒÂ¢Ã‚â‚¬Ã‚â„¢'),
            ('\\u0308', 'ÃƒÅ’Ã‚Ë†'), ('\\u00e8', 'ÃƒÆ’Ã‚Â¨'), ('#038;', ''), ('\\u00f8', 'ÃƒÆ’Ã‚Â¸'),
            ('ÃƒÂ¯Ã‚Â¼Ã‚Â', '/'), ('\\u00e1', 'ÃƒÆ’Ã‚Â¡'), ('&#8211;', '-'), ('&#8220;', 'ÃƒÂ¢Ã‚â‚¬Ã‚Å“'), ('&#8222;', 'ÃƒÂ¢Ã‚â‚¬Ã‚Å¾'),
            ('&#8217;', 'ÃƒÂ¢Ã‚â‚¬Ã‚â„¢'), ('&#8230;', 'ÃƒÂ¢Ã‚â‚¬Ã‚Â¦'), ('\\u00bc', 'Ãƒâ€šÃ‚Â¼'), ('\\u00bd', 'Ãƒâ€šÃ‚Â½'), ('\\u00be', 'Ãƒâ€šÃ‚Â¾'),
            ('\\u2153', 'ÃƒÂ¢Ã‚â€¦Ã‚â€œ')):
            try:
                s = s.replace(*t)
            except:
                pass
        # Umlaute HTML konvertieren
        for h in (('\\/', '/'), ('&#x26;', '&'), ('&#039;', "'"), ("&#39;", "'"),
            ('&#xC4;', 'ÃƒÆ’Ã‚â€ž'), ('&#xE4;', 'ÃƒÆ’Ã‚Â¤'), ('&#xD6;', 'ÃƒÆ’Ã‚â€“'), ('&#xF6;', 'ÃƒÆ’Ã‚Â¶'),
            ('&#xDC;', 'ÃƒÆ’Ã‚Å“'), ('&#xFC;', 'ÃƒÆ’Ã‚Â¼'), ('&#xDF;', 'ÃƒÆ’Ã‚Å¸') , ('&#xB2;', 'Ãƒâ€šÃ‚Â²'),
            ('&#xDC;', 'Ãƒâ€šÃ‚Â³'), ('&#xBC;', 'Ãƒâ€šÃ‚Â¼'), ('&#xBD;', 'Ãƒâ€šÃ‚Â½'), ('&#xBE;', 'Ãƒâ€šÃ‚Â¾'),
            ('&#8531;', 'ÃƒÂ¢Ã‚â€¦Ã‚â€œ')):
            try:
                s = s.replace(*h)
            except:
                pass
        try:
            re.sub(u'ÃƒÆ’Ã‚Â©', 'ÃƒÆ’Ã‚Â©', s)
            re.sub(u'ÃƒÆ’Ã‚â€°', 'ÃƒÆ’Ã‚â€°', s)
            # kill all other unicode chars
            r = re.compile(r'[^\W\d_]', re.U)
            r.sub('', s)
        except:
            pass
        return s

    @staticmethod
    def parse(sHtmlContent, pattern, iMinFoundValue=1, ignoreCase=False):
        aMatches = None
        if sHtmlContent:
            sHtmlContent = cParser.replaceSpecialCharacters(sHtmlContent)
            if ignoreCase:
                aMatches = re.compile(pattern, re.DOTALL | re.I).findall(sHtmlContent)
            else:
                aMatches = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
            if len(aMatches) >= iMinFoundValue:
                return True, aMatches
        return False, aMatches

    @staticmethod
    def replace(pattern, sReplaceString, sValue):
        return re.sub(pattern, sReplaceString, sValue)

    @staticmethod
    def search(sSearch, sValue):
        return re.search(sSearch, sValue, re.IGNORECASE)

    @staticmethod
    def escape(sValue):
        return re.escape(sValue)

    @staticmethod
    def getNumberFromString(sValue):
        pattern = '\\d+'
        aMatches = re.findall(pattern, sValue)
        if len(aMatches) > 0:
            return int(aMatches[0])
        return 0

    @staticmethod
    def urlparse(sUrl):
        return urlparse(sUrl.replace('www.', '')).netloc.title()

    @staticmethod
    def urlDecode(sUrl):
        return unquote(sUrl)

    @staticmethod
    def urlEncode(sUrl, safe=''):
        return quote(sUrl, safe)

    @staticmethod
    def quote(sUrl):
        return quote(sUrl)

    @staticmethod
    def unquotePlus(sUrl):
        return unquote_plus(sUrl)

    @staticmethod
    def quotePlus(sUrl):
        return quote_plus(sUrl)

    @staticmethod
    def B64decode(text):
        import base64
        b = base64.b64decode(text).decode('utf-8')
        return b


class cUtil:
    @staticmethod
    def removeHtmlTags(sValue, sReplace=''):
        p = re.compile(r'<.*?>')
        return p.sub(sReplace, sValue)

    @staticmethod
    def unescape(text): #Todo hier werden Fehler angezeigt
        def fixup(m):
            text = m.group(0)
            if not text.endswith(';'): text += ';'
            if text[:2] == '&#':
                try:
                    if text[:3] == '&#x':
                        return unichr(int(text[3:-1], 16))
                    else:
                        return unichr(int(text[2:-1]))
                except ValueError:
                    pass
            else:
                try:
                    text = unichr(name2codepoint[text[1:-1]])
                except KeyError:
                    pass
            return text

        if isinstance(text, str):
            try:
                text = text.decode('utf-8')
            except Exception:
                try:
                    text = text.decode('utf-8', 'ignore')
                except Exception:
                    pass
        return re.sub("&(\\w+;|#x?\\d+;?)", fixup, text.strip())

    @staticmethod
    def cleanse_text(text):
        if text is None: text = ''
        text = cUtil.removeHtmlTags(text)
        return text

    @staticmethod
    def evp_decode(cipher_text, passphrase, salt=None):
        if not salt:
            salt = cipher_text[8:16]
            cipher_text = cipher_text[16:]
        key, iv = cUtil.evpKDF(passphrase, salt)
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
        plain_text = decrypter.feed(cipher_text)
        plain_text += decrypter.feed()
        return plain_text.decode("utf-8")

    @staticmethod
    def evpKDF(pwd, salt, key_size=32, iv_size=16):
        temp = b''
        fd = temp
        while len(fd) < key_size + iv_size:
            h = hashlib.md5()
            h.update(temp + pwd + salt)
            temp = h.digest()
            fd += temp
        key = fd[0:key_size]
        iv = fd[key_size:key_size + iv_size]
        return key, iv


def valid_email(email): #ToDo: Funktion in Settings / Konten aktivieren
    # Email Muster
    #pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'

    # \xc3\x9cberpr\xc3\xbcfen der EMail-Adresse mit dem Muster
    if re.match(pattern, email):
        return True
    else:
        return False


