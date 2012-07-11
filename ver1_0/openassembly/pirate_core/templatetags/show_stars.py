import math, re

from django.template import Library, Node, TemplateSyntaxError, VariableDoesNotExist, resolve_variable
from django.conf import settings

register = Library()

DIV_TEMPLATE	= "<div id=\"star_strip_%s\">"
END_DIV_TEMPLATE= "</div>"
IMG_TEMPLATE	= "<img border=\"0\" src=\"%s\" alt=\"%s\"/>"
EX_IMG_TEMPLATE	= "<img onClick=\"javascript: hoverStar(%s, %s);\" onmouseout=\"javascript: restoreStar(%s);\" onmouseover=\"javascript: clickStar('%s', %s, %s);\" border=\"0\" src=\"%s\" alt=\"%s\"/>"
STARS = {
	0.0:	("No Star", "/static/images/star_0.0.gif"),
	0.25:	("Quarter Star", "/static/images/star_0.25.gif"),
	0.5:	("Half Star", "/static/images/star_0.5.gif"),
	0.75:	("Three Quarter Star", "/static/images/star_0.75.gif"),
	1.0:	("Full Star", "/static/images/star_1.0.gif")
}
ROUNDERS = {
	"full": 1,
	"half": 2,
	"quarter": 4
}
CMD_PATTERN	= re.compile("^show_stars (.*) of (\d*) round to (%s)$" % "|".join(ROUNDERS))
EX_CMD_PATTERN	= re.compile("^show_stars (.*) of (\d*) round to (%s) on change call (\w*) with (.*)$" % "|".join(ROUNDERS))
JS_TEMPLATE = """
<script type="text/javascript">

var starSaves = new Hash();

function hoverStar(id, pos)
{
    
	var starStrip = $('star_strip_' + id);
	    if (starSaves.keys().indexOf(id) == -1)
	    {
		    var starSave = new Array();
		    var imgs = starStrip.select("img")
		    for (var i = 0; i < imgs.length; i++)
		    {
			    starSave[starSave.length] = imgs[i].src;
			    if (i < pos)
				    imgs[i].src = "/static/images/star_1.0.gif";
			    else
				    imgs[i].src = "/static/images/star_0.0.gif";
			
		    }
		    starSaves.set(id, starSave);
	    }
	    
	}
};

function clickStar(chainTo, id, pos)
{
	try
	{
        eval(chainTo + '(' + id  + ', ' + pos + ');');
	}
	catch (err)
	{
        console.log(err);

	}
	var starStrip = $('star_strip_' + id);
	var imgs = starStrip.select("img")
	for (var i = 0; i < imgs.length; i++)
	{
		if (i < pos)
			imgs[i].src = "/static/images/star_1.0.gif";
		else
			imgs[i].src = "/static/images/star_0.0.gif";
		
	}
	starSaves.unset(id);
};

function restoreStar(id)
{
	srcs = starSaves.get(id);
	if (srcs == undefined)
		return;
	var starStrip = $('star_strip_' + id);
	var imgs = starStrip.select("img");
	for (var i = 0; i < srcs.length; i++)
	{
		imgs[i].src = srcs[i];
	}
	starSaves.unset(id);
};


</script>
"""

class ShowStarsNode(Node):
	""" Default rounding is to the whole unit """
	def __init__(self, stars, total_stars, round_to, handler=None, identifier=None):
		self.stars = stars
		self.total_stars = int(total_stars)
		self.rounder = ROUNDERS[round_to.lower()]
		self.handler = handler
		self.identifier = identifier

	def merge_star(self, pos, fraction, identifier):
		alt, src = STARS[fraction]
		if self.handler:
			pos += 1
			return EX_IMG_TEMPLATE % (identifier, pos, identifier, self.handler, identifier, pos, settings.MEDIA_URL + src, alt)
		else:
			return IMG_TEMPLATE % (settings.MEDIA_URL + src, alt)

	def render(self, context):
		try:
			stars = resolve_variable(self.stars, context)
		except VariableDoesNotExist:
			try:
				stars = float(self.stars)
			except:
				return ""
		try:
			identifier = resolve_variable(self.identifier, context)
		except VariableDoesNotExist:
			identifier = self.identifier

		stars = round(stars * self.rounder) / self.rounder
		fraction, integer = math.modf(stars)
		output = []

		if self.handler:
			output.append(DIV_TEMPLATE % identifier)
		for i in range(self.total_stars):
			if i < integer:
				output.append(self.merge_star(i, 1.0, identifier))
			elif i == integer and fraction:
				output.append(self.merge_star(i, fraction, identifier))
			else:
				output.append(self.merge_star(i, 0.0, identifier))
		if self.handler:
			output.append(END_DIV_TEMPLATE)

		return "".join(output)

class ShowStarsScriptNode(Node):
	def render(self, context):
		return JS_TEMPLATE

def do_show_stars(parser, token):
	def syntax_error():
		raise TemplateSyntaxError("example: show_stars <value> of <total> round to %s [on change call <handler> with <identifier>]" % "|".join(ROUNDERS))
	args = token.contents.split()
	if len(args) == 7:
		match = CMD_PATTERN.match(token.contents)
	elif len(args) == 13:
		match = EX_CMD_PATTERN.match(token.contents)
	else:
		syntax_error()
	if not match:
		syntax_error()
	return ShowStarsNode(*match.groups())   

def do_show_stars_script(parser, token):
	return ShowStarsScriptNode()

register.tag("show_stars", do_show_stars)
register.tag("show_stars_script", do_show_stars_script)
