#!/usr/bin/env python
# encoding: UTF-8

"""
This file is part of commix project (http://commixproject.com).
Copyright (c) 2014-2017 Anastasios Stasinopoulos (@ancst).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
For more see the file 'readme/COPYING' for copying permission.
"""

import sys
import urllib2

from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

def do_check(url):
  """
  This functinality is based on Filippo's Valsorda script [1]
  which uses HEAD requests (with fallback in case of 405) 
  to follow the redirect path up to the real URL.
  ---
  [1] https://gist.github.com/FiloSottile/2077115
  """
  class HeadRequest(urllib2.Request):
      def get_method(self):
          return "HEAD"

  class HEADRedirectHandler(urllib2.HTTPRedirectHandler):
      """
      Subclass the HTTPRedirectHandler to make it use our 
      HeadRequest also on the redirected URL
      """
      def redirect_request(self, req, fp, code, msg, headers, newurl): 
          if code in (301, 302, 303, 307):
            newurl = newurl.replace(' ', '%20') 
            newheaders = dict((k,v) for k,v in req.headers.items()
                              if k.lower() not in ("content-length", "content-type"))
            return HeadRequest(newurl, 
                               headers = newheaders,
                               origin_req_host = req.get_origin_req_host(), 
                               unverifiable = True
                               ) 
          else: 
            err_msg = str(urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)).replace(": "," (")
            print settings.print_error_msg(err_msg + ").")
            sys.exit(0)
              
  class HTTPMethodFallback(urllib2.BaseHandler):
    """
    Fallback to GET if HEAD is not allowed (405 HTTP error)
    """
    def http_error_405(self, req, fp, code, msg, headers): 
      fp.read()
      fp.close()

      newheaders = dict((k,v) for k,v in req.headers.items() if k.lower() not in ("content-length", "content-type"))
      return self.parent.open(urllib2.Request(req.get_full_url(), 
                              headers = newheaders, 
                              origin_req_host = req.get_origin_req_host(), 
                              unverifiable = True)
                              )

  # Build our opener
  opener = urllib2.OpenerDirector() 
  for handler in [urllib2.HTTPHandler, 
                  urllib2.HTTPDefaultErrorHandler,
                  HTTPMethodFallback, 
                  HEADRedirectHandler,
                  urllib2.HTTPErrorProcessor, 
                  urllib2.HTTPSHandler]:
      opener.add_handler(handler())

  response = opener.open(HeadRequest(url))
  redirected_url = response.geturl()
  return redirected_url