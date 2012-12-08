

function spectrumvote(idk, pos, user_pk, obj_pk, ctype_pk){

$.post("/spectrumvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL === true){
           $("#registration_simplebox").simplebox();
      }
      if(data.FAIL !== true){
        load_usersaltcache('#temp_check', user_pk, obj_pk, ctype_pk);
        $('#spectrum_vote').html(' - ' + data.votetype);
      }
      }, "json");
}

function add_platform(ctype, object_pk){ 
$.post("/add_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL === true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
}

function remove_platform(ctype, object_pk){ 
$.post("/remove_platform/", {ctype:ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL === true){         
           $("#registration_simplebox").simplebox();
      }
    }, "json");
}

function starvote(idk, pos, user_pk, obj_pk, ctype_pk){ 
$.post("/starvote/", {vote: pos, pk: idk},
  function(data) {
      if(data.FAIL === true){     
           $("#registration_simplebox").simplebox();
      }
      if(data.FAIL !== true){
        load_usersaltcache('#temp_check', user_pk, obj_pk, ctype_pk);
      }

    }, "json");
}

function flagvote(idk,user,value,flag_type, div_id, img_id){ 
$.post("/flagvote/", {vote: value, pk: idk, user:user, flag_type:flag_type},
  function(data) {
      if(data.FAIL !== true){
          changeImgSrc(data.imgsrc,img_id);
          changeText(data.count,div_id);
      }
 }, "json");
}

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
}

function changeImgSrc(text,div_id)
{
 elem = document.getElementById(div_id);
 elem.src = text;
}

function js_redirect(location)
{
    window.location = location;
}

function add_tag(tag, obj_id, c_type, app_type){
$.post("/add_tag/", {tag: tag, obj: obj_id, c_type:c_type, app_type:app_type },
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

function add_platform(ctype, object_pk){
$.post("/add_platform/", {ctype: ctype, object_pk: object_pk},
  function(data) {
      if(data.FAIL !== true){
      }
 }, "json");
}

function support(add, subscribed, user){
  if(add === true){
      $.post("/add_support/", {subscribed: subscribed, user: user},
        function(data) {
            if(data.FAIL !== true){
              //$('#mygroup').append(data.group);
              history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
              getContent({});
            }
       }, "json");
  }
  if(add === false){
      $.post("/remove_support/", {subscribed: subscribed, user: user},
        function(data) {
            if(data.FAIL !== true){
              //$('#mygroup').append(data.group);
              history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
              getContent({});
            }
       }, "json");
  }
}

function add_group(topic, user){
$.post("/add_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        //$('#mygroup').append(data.group);
        //history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
        //getContent();
        //$('.thumbnail_list').prepend(data.group);
        load_usersaltcache('#mygroups', data.user, '', '',
            {'hash': '/p/mygroups/d-mygroups/p-1'});
        console.log(data);
        load_usersaltcache('#oa_addgroup', data.user, data.object_pk , data.ctype,
            {'hash': '/p/addgroup'});
      }
 }, "json");
}

function remove_group(topic, user){
$.post("/remove_group/", {topic: topic, user: user},
  function(data) {
      if(data.FAIL !== true){
        //$(data.group).remove();
        //history.pushState({load:true, module:'Reload', url: data.redirect}, '', data.redirect);
        //getContent();
        //$(data.group).remove();
        load_usersaltcache('#mygroups', data.user, '', '',
            {'hash': '/p/mygroups/d-mygroups/p-1'});
        console.log(data);
        load_usersaltcache('#oa_addgroup', data.user, data.object_pk , data.ctype,
            {'hash': '/p/addgroup'});
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
                  js_redirect('/p/content_delete');
                }
             }, "json");
     }
}

function ScrollToElement(theElement)
{

  var selectedPosX = 0;
  var selectedPosY = 0;
              
  while(theElement !== null){
    selectedPosX += theElement.offsetLeft;
    selectedPosY += theElement.offsetTop;
    theElement = theElement.offsetParent;
  }

 window.scrollTo(selectedPosX,selectedPosY);

}

function ranked_vote_confirm(obj_pk, val){
  if(val){
    $.post("/confirm_ranked_vote/", {object_pk: obj_pk},
    function(data) {
        if(data.FAIL !== true){
            $("#confirm_button").fadeOut('fast');
            changeText(data.confirm_button,'confirm_button');
            $("#confirm_button").fadeIn('fast');
      }
   }, "json");
  }
  else{
    $.post("/del_confirm_ranked_vote/", {object_pk: obj_pk},
    function(data) {
        if(data.FAIL !== true){
            $("#confirm_button").fadeOut('fast');
            changeText(data.confirm_button,'confirm_button');
            $("#confirm_button").fadeIn('fast');
        }
   }, "json");
  }
  
}

function addObject(e){
    e.preventDefault();
    var o = {};
    var a = $(e.target).serializeArray();
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
    var form = o;
    $.post("/load_page/", {form: form, hash: location.href},
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
                $.get("/side_effect/", {key: location.href, side_effect: se, usc_pk: data.output[item].usc_pk, obj_pk: data.output[item].obj_pk},
                  function(data2) {
                      for(var item in data2.output){
                        if(data2.output[item].type == 'redirect'){
                            history.pushState({load:true, module:'leave'}, '', data2.output[item].html);
                            //remove current tab
                            var curtab = $('#current_tab').html();
                            $('#tabholdertab' + curtab).remove();
                            $('#page' + curtab).remove();
                            sessionStorage.removeItem(curtab);
                            $('#current_tab').html('');
                            $('#overlay').hide();
                            $("html").css("overflow", "auto");
                            getContent({});
                        }
                        if(data2.output[item].type == 'after'){
                            $(data2.output[item].div).after(data2.output[item].html);
                        }
                        else if(data2.output[item].type == 'before'){
                            $(data2.output[item].div).before(data2.output[item].html);
                        }
                        else if(data2.output[item].type == 'prepend'){
                            $(data2.output[item].div).prepend(data2.output[item].html);
                        }
                        else if(data2.output[item].type == 'append'){
                            $(data2.output[item].div).append(data2.output[item].html);
                        }
                        else if(data2.output[item].type == 'html'){
                            $(data2.output[item].div).html(data2.output[item].html);
                        }
                        else{
                          $(data2.output[item].div).html(data2.output[item].html);
                        }
                        /*if(data2.output[item].scroll_to === true){
                                var hash = location.href;
                                var dom = $('#domain').html();
                                var tempkey = hash.replace(dom, '');
                                tempkey = tempkey.replace('http:', '');
                                tempkey = tempkey.replace(/\//g,"");
                                $(data2.output[item].div).slideto({'div_offset': -400, 'thadiv': '#page' + tempkey, 'highlight_color':'#d6e3ec'});                        
                        }*/
                    }
                    //hrefLess();
                }, "json");
            }
          //if(data.POST){}
        }, "json");

  }

function tabQueue() {
    var window_width = $(window).width();
        ruler = $('#tab_ruler');
        ruler_width = ruler.width();
        min_win = window_width - 300;
        num_tabs = $('#the_queue .tab').length;
        tab_iter = $('#tab_queue .tab_iterate');
    
    // check to see if the tabs are being overlapped by the queue
    if (ruler_width > min_win) {
        // move tabs to queue
        var last_tab = $('#tab_ruler .tab').last();
        $('#the_queue').append(last_tab);
    } else if ( (min_win - 162 ) > ruler_width) {
        // move tabs back to taskbar
        var last_tab = $('#the_queue .tab').last();
        $('#tab_ruler').append(last_tab);
    }
    
    if (num_tabs > 0) {
        tab_iter.text(num_tabs);
    } else {
        tab_iter.text('No');
    }
    
}


// remember how many tabs were in queue on doc load
function rememberTabs() {
    var window_width = $(window).width();
        ruler = $('#tab_ruler');
        ruler_width = ruler.width();
        min_win = window_width - 157;
        num_tabs = $('#pages .page').length;
        old_width = $('#tab_width').text();
    
    num_of_times_to_fire = Math.ceil( num_tabs - ( Math.abs(old_width - window_width) / 162 ) );
    for (i=-2; i<=num_of_times_to_fire; i++) {
        tabQueue();
    }
}

function load_usersaltcache(div, user, obj_pk, ctype_pk, options){
    var h;
    if(options !== undefined){
      if(options.hash === undefined || options.hash === null){
        h = location.href;
      }
      else{
        h = options.hash;
      }
    }
    else{
        h = location.href;
    }
    console.log('salt caching' + h);
    console.log(options);
    $.get("/load_usersaltcache/", {div: div, hash: h, user: user, obj_pk: obj_pk, ctype_pk: ctype_pk},
        function(data) {
                for(var item in data.output){
                    if(data.output[item].type == 'prepend'){
                      $(data.output[item].div).prepend(data.output[item].html);
                    }
                    if(data.output[item].type == 'append'){
                        $(data.output[item].div).append(data.output[item].html);
                    }
                    if(data.output[item].type == 'html'){
                        console.log($(data.output[item].div).html());
                        $(data.output[item].div).html(data.output[item].html);
                    }
                    if(data.output[item].toggle === true){
                        $(data.output[item].div).slideToggle();
                    }
                    //now we need to gather side-effect data and render all side-effects
                    var se = $(data.output[item].div + '_side_effect').html();
                    $.get("/side_effect/", {key: location.href, side_effect: se, usc_pk: data.output[item].usc_pk, obj_pk: data.output[item].obj_pk},
                      function(data2) {
                          for(var item in data2.output){
                            if(data2.output[item].type == 'redirect'){
                                  history.pushState({load:true, module:'Reload'}, '', data2.output[item].html);
                                  getContent({});
                            }
                            if(data2.output[item].type == 'after'){
                                $(data2.output[item].div).after(data2.output[item].html);
                            }
                            if(data2.output[item].type == 'before'){
                                $(data2.output[item].div).before(data2.output[item].html);
                            }
                            if(data2.output[item].type == 'prepend'){
                                $(data2.output[item].div).prepend(data2.output[item].html);
                            }
                            if(data2.output[item].type == 'append'){
                                $(data2.output[item].div).append(data2.output[item].html);
                            }
                            if(data2.output[item].type == 'html'){
                                $(data2.output[item].div).html(data2.output[item].html);
                            }
                            if(data2.output[item].scroll_to === true){
                                var hash = location.href;
                                var dom = $('#domain').html();
                                var tempkey = hash.replace(dom, '');
                                tempkey = tempkey.replace('http:', '');
                                tempkey = tempkey.replace(/\//g,"");
                                $(data2.output[item].div).slideto({'div_offset': -400, 'thadiv': '#page' + tempkey, 'highlight_color':'#d6e3ec'});
                            }
                        }
                        //hrefLess();
                    }, "json");
                }
            //if(data.POST){}
        }, "json");

  }


function getContent(options){

//            if (currentXhr != null && typeof currentXhr != 'undefined') {
//                currentXhr.abort();
//            }
    d = {};
    d['hash'] = location.href;
    d['empty'] = ($('#content').is(':empty'));
    d['width'] = screen.width;
    d['height'] = screen.height;
    var tempkey = get_key(d['hash']);
    var ss = sessionStorage.getItem(tempkey);
    var current = sessionStorage.getItem('current');
    console.log(tempkey);
    var render;
    console.log('test');
    console.log(ss);
    if(ss === null || 'reload' in options || ss !== location.href){
      $.get("/load_page/", d,
        function(OAdata) {
           var render = OAdata.rendertype;
           if(OAdata.FAIL !== true){
                  for(var item in OAdata.output){
                      if(('reload' in options|| ss !== null && ss !== location.href) && OAdata.output[item].div == '#tab_ruler'){

                      }
                      else{
                          if(OAdata.output[item].div == '#pages' && ('reload' in options || ss !== null && ss !== location.href)){
                              console.log('#page' + tempkey);
                              console.log('so american...'  + $('#page' + tempkey).html());
                              $('#page' + tempkey).replaceWith(OAdata.output[item].html);
                          }
                          else{
                            if(OAdata.output[item].type == 'prepend'){
                              $(OAdata.output[item].div).prepend(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].type == 'append'){
                                $(OAdata.output[item].div).append(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].type == 'html'){
                                $(OAdata.output[item].div).html(OAdata.output[item].html);
                            }
                            if(OAdata.output[item].div == '#pages' && !('reload' in options || ss !== null && ss !== location.href)){
                                //set the current div
                                toggleMinMax(tempkey, render, location.href, 'popstate' in options);
                                sessionStorage.setItem('current', tempkey);
                            }
                          }
                      }
                  }
                //$("#content").append(data.POST);
                
                //location.hash = data.url
            }
            if(OAdata.FAIL === true){
                alert('Some problems were detected.');
                js_redirect('/404.html?');
            }
            sessionStorage.setItem(tempkey, location.href);
            //hrefLess();
            rememberTabs();


          //if(OAdata.scroll_to !== null){
          //  $(OAdata.scroll_to).slideto({'slide_duration': "fast", 'highlight': false});
          //}
          //else{
          //  $('html').slideto({'slide_duration': "fast", 'highlight': false});
          //}
       }, "json");

    }
    if (ss !== undefined && ss !== null && !('reload' in options  || ss !== null && ss !== location.href) && render != 'message'){
        toggleMinMax(tempkey, render, location.href, 'popstate' in options);
    }
}

function get_key(hash){
  var dom = $('#domain').html();
  var input = hash.replace(dom, '');
    input = input.replace('http:', '');
    //tempkey = tempkey.replace(/\//g,"");
    var regex = /\/p\/\w*\/k-[\w-]*/g;
    if(regex.test(input)) {
      var matches = input.match(regex);
      return matches[0].replace(/\//g,""); //cannot have / characters in key
    } else {
      return input.replace(/\//g,"");
    }
}


function sort_dashboard(sorted){
  
  $.post("/sort_board/", {sorted: sorted},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //$('#ballot_complete{{plat.pk}}').html(data.complete_perc);
      }
  }, "json");
}

function adjustchat(obj_pk){
    $('#chat_ctrl' + obj_pk).css('marginTop', $('#' + obj_pk).height()-45 + "px");
}


//obj_pk is actually dashobj pk
function increase_zoom(obj_pk, dim, path, dash_id, type, obj){
  
  $.post("/increase_zoom/", {object_pk: obj_pk, dimension: dim},
  function(data) {
      if(type == 'Chat'){
        $('#user_container' + obj).css('height', $('#' + obj_pk).height()-30 + "px");
        adjustchat(obj_pk);
      }
      if(type == 'Stream' || type == 'Location'){
        refresh_size(path, dash_id, obj_pk);
      }
  }, "json");
}
//obj_pk is actually dashobj pk
function decrease_zoom(obj_pk, dim, path, dash_id, type, obj){
  
  $.post("/decrease_zoom/", {object_pk: obj_pk, dimension: dim},
  function(data) {
      if(type == 'Chat'){
        adjustchat(obj_pk);
        $('#user_container' + obj).css('height', $('#' + obj_pk).height()-30 + "px");
      }
      if(type == 'Stream' || type == 'Location'){
        refresh_size(path, dash_id, obj_pk);
      }
  }, "json");
}

function resort_dashboard(dash_id, sort_key, dashobjpk){
  
  $.post("/resort_board/", {dashboard_id: dash_id, sort_key: sort_key, dashobj: dashobjpk},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //chat window should be resized
          refresh_dashboard(data.plank, data.dash_id, dashobjpk);
      }
  }, "json");
}

function refresh_dashboard(path, dash_id, dashobjpk, start, end){
  $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'refresh', boardname: null, start: start, end: end, dashobj: dashobjpk },
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          //chat window should be resized
          if(data.rendertype == 'chat'){
              $('#chat_ctrl' + data.dashpk).css('marginTop', data.height + "px");
          }
          else{
            $('#' + data.dashpk).html(data.html);
            //hrefLess();
            //ui.item.addClass('dragging').removeClass('');
            //ui.item.addClass('dragging').addClass('panel');

          }
          $('#panels').masonry('reload');
      }

  }, "json");

}

function refresh_size(path, dash_id, dashobjpk){
  //special case for non-logged in user

      $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'refresh', boardname: null, dashobj: dashobjpk},
      function(data) {
          if(data.FAIL === true){
             //$(ui.item).fadeOut('slow', function() {
              //    $(ui.sender).append(ui.item);
              //    $(ui.item).fadeIn('slow');
              //});
          }
          if(data.FAIL === false){
              //chat window should be resized
              if(data.rendertype == 'chat'){
                $('#chat_ctrl' + data.dashpk).css('marginTop', data.height + "px");
              }
              else{
                $('#' + data.dashpk).html(data.html);
                $('#' + data.dashpk).removeClass('pwide' + data.dashzoom_x );
                $('#' + data.dashpk).removeClass('pwide' + data.dashzoom_x + 2);
                $('#' + data.dashpk).removeClass('ptall' + data.dashzoom_y );
                $('#' + data.dashpk).removeClass('ptall' + data.dashzoom_y + 2);

                $('#' + data.dashpk).addClass('pwide' + data.dashzoom_x + 1);
                $('#' + data.dashpk).addClass('ptall' + data.dashzoom_y + 1);

              }
              $('#panels').masonry('reload');
              //hrefLess();

          }
      }, "json");
  }


function push_dashboard(path, dash_id, boardname){
  $.post("/add_board/", {path: path, dashboard_id: dash_id, type: 'add', boardname: boardname},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          $('#panels').prepend(data.html);
          $('#panels').masonry('reload');
          $('#tutorial').hide();
          $('#youtube').remove();
          //hrefLess();
      }
  }, "json");
}

function delete_dashboard(obj_pk){
  
  $.post("/del_board/", {object_pk: obj_pk},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
        $('#' + obj_pk).remove();
        $('#panels').masonry('reload');
      }
  }, "json");
}


function allowPush(e, url, that) {
    return (!e.ctrlKey && !e.metaKey && !e.altKey && !e.shiftKey &&
        url != ''  && url.indexOf('#')==-1 && url.indexOf('javascript') == -1 && url.indexOf('http://') == -1 && url.indexOf('https://') == -1 && (typeof that.attr('target') == 'undefined' || that.attr('target') == '') 
        && !that.hasClass('nobbq') && typeof $.data(that.get(0), 'events') == 'undefined' && typeof disablePush == 'undefined')
}

// Panel resizing
// Down
function downzoom(dashpk, path, dash_id, type, obj){
    var p = $('#' + dashpk);
    if (p.hasClass('ptall3')) {
        return false;
    } else if (p.hasClass('ptall2')) {
        p.removeClass('ptall2').addClass('ptall3');
        p.find('icon-chevron-down').closest('li').addClass('disabled');
        increase_zoom(p.attr('id'), 'Y', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else {
        p.find('.icon-chevron-up').closest('li').removeClass('disabled');
        p.addClass('ptall2');
        increase_zoom(p.attr('id'), 'Y', path, dash_id, type, obj);
        $('#panels').masonry('reload');
    }
}
// Up
function upzoom(dashpk, path, dash_id, type, obj){
    var p = $('#' + dashpk);
    if (p.hasClass('ptall3')) {
        p.find('.icon-chevron-down').closest('li').removeClass('disabled');
        p.removeClass('ptall3').addClass('ptall2');
        decrease_zoom(p.attr('id'), 'Y', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else if (p.hasClass('ptall2')) {
        p.removeClass('ptall2');
        p.find('.icon-chevron-up').closest('li').addClass('disabled');
        decrease_zoom(p.attr('id'), 'Y', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else {
        return false;
    }
}
// Right
function rightzoom(dashpk, path, dash_id, type, obj){
    var p = $('#' + dashpk);
    if (p.hasClass('pwide4')) {
        return false;
    } else if (p.hasClass('pwide3')) {
        p.removeClass('pwide3').addClass('pwide4');
        p.find('.icon-chevron-right').closest('li').addClass('disabled');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide2')) {
        p.removeClass('pwide2').addClass('pwide3');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else {
        p.addClass('pwide2');
        p.find('.icon-chevron-left').closest('li').removeClass('disabled');
        increase_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');
    }
}
// Left
function leftzoom(dashpk, path, dash_id, type, obj){
    var p = $('#' + dashpk);
    if (p.hasClass('pwide4')) {
        p.find('.icon-chevron-right').closest('li').removeClass('disabled');
        p.removeClass('pwide4').addClass('pwide3');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide3')) {
        p.removeClass('pwide3').addClass('pwide2');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else if (p.hasClass('pwide2')) {
        p.removeClass('pwide2');
        p.find('icon-chevron-left').closest('li').addClass('disabled');
        decrease_zoom(p.attr('id'), 'X', path, dash_id, type, obj);
        $('#panels').masonry('reload');

    } else {
        return false;
    }
}


function toggleMinMax(t, render, url, popstate){
    var curtab = sessionStorage.getItem('current');
    var keepif = (curtab === null);
    var nempty = $('#pages').find('.current').length === 0;

    if(nempty){
        $('#overlay').show();
    }

    if(!nempty && t == curtab){
        $('#overlay').hide();
        console.log('pushing state 1');
        if(!popstate){history.pushState({load:true, module:'leave', url: '/'}, '', '/');}
        $("html").css("overflow", "auto");

    }

    if(t != curtab){

        if(render == 'message'){
            var tarb = $('#tab' + t).position();
            if(tarb !== null){
              $('#page' + t).css('left', tarb.left);
            }
            $('#overlay').hide();
        }
        else{
            $('#overlay').show();
            $("html").css("overflow", "hidden");
        }

        //add new pagev

        console.log(history.state);
        var dom = $('#domain').html();
        var tempkey = sessionStorage.getItem(t);
        if(tempkey !== null){
          tempkey = tempkey.replace(dom, '');
          tempkey = tempkey.replace('http://', '');
          console.log('pushing state 2' + popstate + ' url=' + tempkey);
        }
        else{
          tempkey = url;
        }
        if(!popstate){history.pushState({load:true, module:'leave', url: tempkey}, '', tempkey);}
        $('#page' + t).show();
        $('#tab' + t).addClass('current-icon');
        $('#page' + t).addClass('current');
        //set the current div
        sessionStorage.setItem('current', t);
        if(render == 'message'){
            $('#page' + t).scrollTo('max');
        
        }
    }
    else{
        //minimze the current object
        sessionStorage.setItem('current', null);
    }
    if(!keepif){
        //remove the old page
        $('#page' + curtab).removeClass('current');
        $('#page' + curtab).hide();
        $('#tab' + curtab).removeClass('current-icon');
    }
}

// Closes/removes Page/Tab
function tabRemove(tab){
    tabobj = $('#tabholdertab' + tab);
    
    //for whatever reason this stopped working...
    //tabobj.fadeTo(600, 0, function(){
    //    tabobj.remove();
    //});
    tabobj.remove();
    $('#page' + tab).remove();
    sessionStorage.removeItem(tab);
    var curtab = sessionStorage.getItem('current');
    if (curtab == tab){
        history.replaceState({load:true, module:'leave', url: '/'}, '', '/');
        $('#current_tab').html('');
        $('#overlay').hide();
        $("html").css("overflow", "auto");
        sessionStorage.setItem('current', null);
    }
    rememberTabs();

    //remove page or not?
};



// Remove's href from anchors and adds them as data attr (so browser status bars don't cover up OA's taskbar)
//need to get rid of this, and instead identify the user agent and only return hrefs to bots we like
function hrefLess() {
    //alert('hefrels');
    $('a').each(function(){
        var t = $(this);
        if(t.attr('id') != 'register'){
            if(typeof t.attr('href') != 'undefined'){
                t.data('href', t.attr('href'));
                t.removeAttr('href');
            }
        }
    });
    //$('a').on('click', function(){
    //   var t = $(this);
    //    if(t.attr('id') != 'register' && t.attr('id') != 'fancybox-close'){
    // //        window.location = $(this).data('href');
    //     }
    // });
}

//minimize all pages
function minimizeAll(){
      curtab = sessionStorage.getItem('current');
      history.pushState({load:true, module:'leave', url: ''}, '', '/');
      if(curtab !== null){
          $('#page' + curtab).removeClass('current');
          $('#page' + curtab).hide();
          $('#tab' + curtab).removeClass('current-icon');

      }
      $('#overlay').hide();
      sessionStorage.setItem('current', null);
      $("html").css("overflow", "auto");

}



//For viewing edits dynamically
function load_patch(obj_pk, patch){
  edit_pk = $('#current_edit' + obj_pk).attr("class");
  edit_num = $('#edit_num' + obj_pk).attr("class");
  $.post("/load_patch/", {obj_pk: obj_pk, edit_num: edit_num, patch: patch},
  function(data) {
      if(data.FAIL === true){
         //$(ui.item).fadeOut('slow', function() {
          //    $(ui.sender).append(ui.item);
          //    $(ui.item).fadeIn('slow');
          //});
      }
      if(data.FAIL === false){
          $('#description' + obj_pk).fadeOut('fast', function() {
            $('#description' + obj_pk).html(data.text);
            $('#description' + obj_pk).fadeIn();
          });
          $('#current_edit' + obj_pk).html(data.next);
          $('#edits' + obj_pk).html(data.ctrl);

          //hrefLess();
      }
  }, "json");

}

if(!String.linkify) {
    String.prototype.linkify = function() {

        // http://, https://, ftp://
        var urlPattern = /\b(?:https?|ftp):\/\/[a-z0-9-+&@#\/%?=~_|!:,.;]*[a-z0-9-+&@#\/%=~_|]/gim;

        // www. sans http:// or https://
        var pseudoUrlPattern = /(^|[^\/])(www\.[\S]+(\b|$))/gim;

        // Email addresses
        var emailAddressPattern = /\w+@[a-zA-Z_]+?(?:\.[a-zA-Z]{2,6})+/gim;

        return this
            .replace(urlPattern, '<a href="$&" target="_blank">$&</a>')
            .replace(pseudoUrlPattern, '$1<a href="http://$2" target="_blank">$2</a>')
            .replace(emailAddressPattern, '<a href="mailto:$&">$&</a>');
    };
}

function EvalSound(soundobj) {
      var thissound=document.getElementById(soundobj);
      thissound.src = thissound.src;
      thissound.play();
}

function sound_toggle(obj){
  if($('#chatsounds' + obj).attr('class')=='true'){
    $('#chatsounds' + obj).attr('class','false');
    $('#soundsctrl' + obj).html("<i class='icon-volume-up icon-white icon-left'></i>Turn On Sounds");
  }
    else{
      $('#chatsounds' + obj).attr('class','true');
      $('#soundsctrl' + obj).html("<i class='icon-volume-off icon-white icon-left'></i>Turn Off Sounds");
    }
}

//CREATES A NOTIFICATION TO THE USER, GENERATED BY SOCKETS
function notify(dict){

    //bit of a hack to easily access the message url though sockets
    if(dict.type == 'message'){
        var htmlmessage = '<a data-href="/p/message/k-'  + dict.message.replace(' said', '') + '">'
        htmlmessage = htmlmessage + '<h4>' + dict.message + '</h4><h3 style="width:65%;float:left;">' + dict.object + '</h3>';
    }
    else{
      var htmlmessage = '<h4>' + dict.message + '</h4><h3 style="width:65%;float:left;">' + dict.object + '</h3>';
    }
    if(dict.type == 'vote'){
        htmlmessage = htmlmessage + '<img src="/static/img/vote_icon.png">'
    }
    if(dict.type == 'comment'){
        htmlmessage = htmlmessage + '<img src="/static/img/comment_icon.png">'
    }
    if(dict.type == 'message'){
        htmlmessage = htmlmessage + '<img src="/static/img/message_icon.png"></a>'
    }
    if($('#dynamic').css('top') == '-200px'){
        $('#dynamic').animate({'top':'32px'},500).delay(3000).animate({'top': '-200px'},500);
    }
    $('#dynamic').html(htmlmessage);    
}


//LOCATION BASED JAVASCRIPT FOR ADDING, DELETING, and LOADING
function createLocation(object_pk, content_type, lat, lon, desc){

  $.post("/create_location/", {object_pk: object_pk, content_type:content_type, lat:lat, lon:lon, desc:desc},
  function(data) {
      if(data.FAIL === false){
        $('.location_desc' + object_pk).fadeOut( function(){
            $('.location_desc' + object_pk).html('<h3>Location Saved</h3>');  
          });
          $('.location_desc' + object_pk).fadeIn( function() {
                $('#currentLocation' + object_pk).fadeOut( function(){
                  $('#currentLocation' + object_pk).html('<span><b>Current Location:</b> ' + desc + "</span><span class='btn' onclick='deleteLocation(" + '"' + object_pk + '"' + ");'>" + '<i class="icon-warning-sign icon-left"></i>Remove</span>');  
                });
                $('#currentLocation' + object_pk).fadeIn();
          });
          $('#currentLocation' + object_pk).fadeIn();

      }
  }, "json");
}

function deleteLocation(object_pk){

  $.post("/delete_location/", {object_pk: object_pk},
  function(data) {
      if(data.FAIL === false){
        $('#currentLocation' + object_pk).fadeOut( function(){
            $('#currentLocation' + object_pk).html(''); 
            $('#currentLocation' + object_pk).fadeIn();
          });

      }
  }, "json");
}

function loadMarkers(object_pk, content_type, start, end, dimension, dashobj_pk){
  $.get("/moar_markers_plz/", {object_pk: object_pk, content_type:content_type, start:start, end:end, dimension:dimension, dashobj_pk:dashobj_pk},
  function(data) {
      if(data.FAIL === false){
        alert('#extramarkers'  + dashobj_pk);
        $('#extramarkers'  + dashobj_pk).append(data.html);
        alert(data.link);
        $('#loadmore' + dashobj_pk).html(data.link);
      }
  }, "json");
}

function refresh(url, div){
    history.replaceState({load:true, module:'Reload', url: url}, '', url);
    getContent({'reload':true, 'div':div});
}