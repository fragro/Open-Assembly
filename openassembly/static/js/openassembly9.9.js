function spectrumvote(idk, pos){ 
$.post("/spectrumvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL == true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
};

function add_platform(ctype, object_pk){ 
$.post("/add_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL == true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
};

function remove_platform(ctype, object_pk){ 
$.post("/remove_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL == true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
}

function starvote(idk, pos){ 
$.post("/starvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL == true){     
           $("#registration_simplebox").simplebox();
      }
    }, "json");
};

function flagvote(idk,user,value,flag_type, div_id, img_id){ 
$.post("/flagvote/", {vote: value, pk: idk, user:user, flag_type:flag_type},
  function(data) {
      if(data.FAIL != true){
          changeImgSrc(data.imgsrc,img_id);
          changeText(data.count,div_id);
      }
 }, "json");
};

function set_loc_by_ip(city,region,country){ 
$.post("/set_loc_by_ip/", {city:city, region:region, country:country},
  function(data) {
      if(data.FAIL !== true){

      }
 }, "json");
}
function changeText(text,div_id)
{
 elem = document.getElementById(div_id);
 elem.innerHTML = text;
};

function changeImgSrc(text,div_id)
{
 elem = document.getElementById(div_id);
 elem.src = text;
};

function js_redirect(location)
{
    window.location.replace( location );
};

function add_tag(tag, obj_id, c_type, app_type){ 
$.post("/add_tag/", {tag: tag, obj: obj_id, c_type:c_type, app_type:app_type },
  function(data) {
      if(data.FAIL != true){
          $("#recommendations").fadeOut('fast');
          $("#tags").fadeOut('fast');
          changeText(data.taglist,'recommendations');
          changeText(data.linktaglist,'tags');
          $("#recommendations").fadeIn('fast');
          $("#tags").fadeIn('fast');

      }
 }, "json");
}

function add_platform(ctype, object_pk){ 
$.post("/add_platform/", {ctype: ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL !== true){
      }
 }, "json");
}

function add_group(topic, user){ 
$.post("/add_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        $('#mygroup').append(data.group);
      }
 }, "json");
}

function remove_group(topic, user){ 
$.post("/remove_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        $(data.group).html('');
      }
 }, "json");
}

function del_tag(tag, obj_id, c_type, app_type){ 
$.post("/del_tag/", {tag: tag, obj: obj_id, c_type:c_type, app_type:app_type },
  function(data) {
      if(data.FAIL !== true){
          $("#recommendations").fadeOut('fast');
          $("#tags").fadeOut('fast');
          changeText(data.taglist,'recommendations');
          changeText(data.linktaglist,'tags');
          $("#recommendations").fadeIn('fast');
          $("#tags").fadeIn('fast');

      }
 }, "json");
}

function checkDelete(ctype_id, obj_id)
{
     if($('#nukecheck').is(':checked')){
         $.post("/objectdelete/", {content_type: ctype_id, object_id: obj_id},
              function(data) {
                if(data.FAIL !== true){
                  js_redirect('content_delete.html');
                }
             }, "json");
     }
}

function ScrollToElement(theElement)
{

  var selectedPosX = 0;
  var selectedPosY = 0;
              
  while(theElement != null){
    selectedPosX += theElement.offsetLeft;
    selectedPosY += theElement.offsetTop;
    theElement = theElement.offsetParent;
  }
                        		      
 window.scrollTo(selectedPosX,selectedPosY);

};

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};

function side_effect_func(data) {
      for(var item in data.output){
        if(data.output[item].type == 'redirect'){
          js_redirect(data.output[item].html); 
        } 
        if(data.output[item].type == 'after'){
            $(data.output[item].div).after(data.output[item].html); 
        } 
        if(data.output[item].type == 'before'){
            $(data.output[item].div).before(data.output[item].html); 
        } 
        if(data.output[item].type == 'prepend'){
            $(data.output[item].div).prepend(data.output[item].html); 
        } 
        if(data.output[item].type == 'append'){
            $(data.output[item].div).append(data.output[item].html); 
        } 
        if(data.output[item].type == 'html'){
            $(data.output[item].div).html(data.output[item].html); 
        }
        if(data.output[item].scroll_to === true){
            $(data.output[item].div).slideto({'highlight_color':'#d6e3ec'});
        }
    }
}

function addObject(e){
    e.preventDefault();
    var form = $(e.target).serializeObject();
    $.post("/load_page/", {form: form, hash: location.hash},
        function(data) {
                for(var item in data.output){
                    if(data.output[item].type == 'prepend'){
                      $(data.output[item].div).prepend(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'append'){
                        $(data.output[item].div).append(data.output[item].html); 
                    } 
                    if(data.output[item].type == 'html'){
                        $(data.output[item].div).html(data.output[item].html); 
                    }
                    if(data.output[item].toggle === true){
                        $(data.output[item].div).slideToggle();
                    }
                    //now we need to gather side-effect data and render all side-effects
                    var se = $(data.output[item].div + '_side_effect').html();
                    $.get("/side_effect/", {key: location.hash, side_effect: se, usc_pk: data.output[item].usc_pk, obj_pk: data.output[item].obj_pk},
                      side_effect_func(data), "json");
                }
            //if(data.POST){}  
        }, "json");
    };