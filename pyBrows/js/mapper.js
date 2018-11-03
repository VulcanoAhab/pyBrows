var cartesian={

  simpleBox:function(element){
    var rect=element.getBoundingClientRect();
    scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    return {
      top: rect.top + scrollTop,
      left: rect.left + scrollLeft,
      width:rect.width,
      height:rect.height
        };
  }
}

var FlatMap={
  base:[],
  base_map:[],
  inventory:function (documentObj){
    this.base=documentObj.getElementsByTagName("*");
    for (b=0; b<this.base.length; ++b){
      var element=this.base[b];
      var rect=cartesian.simpleBox(element);
      var mapObj={
        "element":element,
        "top":rect.top,
        "left":rect.left,
        "width":rect.width,
        "height":rect.height
      };
      base_map.push(mapObj);
    }
  }
}
