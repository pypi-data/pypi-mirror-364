"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2669"],{13539:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{Bt:()=>l});a(39710);var o=a(57900),i=a(3574),n=a(43956),s=e([o]);o=(s.then?(await s)():s)[0];const d=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],l=e=>e.first_weekday===n.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,i.L)(e.language)%7:d.includes(e.first_weekday)?d.indexOf(e.first_weekday):1;r()}catch(d){r(d)}}))},60495:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{G:()=>l});var o=a(57900),i=a(28105),n=a(58713),s=e([o,n]);[o,n]=s.then?(await s)():s;const d=(0,i.Z)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),l=(e,t,a,r=!0)=>{const o=(0,n.W)(e,a,t);return r?d(t).format(o.value,o.unit):Intl.NumberFormat(t.language,{style:"unit",unit:o.unit,unitDisplay:"long"}).format(Math.abs(o.value))};r()}catch(d){r(d)}}))},58713:function(e,t,a){a.a(e,(async function(e,r){try{a.d(t,{W:()=>u});a(87799);var o=a(7722),i=a(66233),n=a(41238),s=a(13539),d=e([s]);s=(d.then?(await d)():d)[0];const c=1e3,p=60,h=60*p;function u(e,t=Date.now(),a,r={}){const d=Object.assign(Object.assign({},g),r||{}),l=(+e-+t)/c;if(Math.abs(l)<d.second)return{value:Math.round(l),unit:"second"};const u=l/p;if(Math.abs(u)<d.minute)return{value:Math.round(u),unit:"minute"};const b=l/h;if(Math.abs(b)<d.hour)return{value:Math.round(b),unit:"hour"};const v=new Date(e),_=new Date(t);v.setHours(0,0,0,0),_.setHours(0,0,0,0);const m=(0,o.j)(v,_);if(0===m)return{value:Math.round(b),unit:"hour"};if(Math.abs(m)<d.day)return{value:m,unit:"day"};const y=(0,s.Bt)(a),x=(0,i.z)(v,{weekStartsOn:y}),f=(0,i.z)(_,{weekStartsOn:y}),w=(0,n.p)(x,f);if(0===w)return{value:m,unit:"day"};if(Math.abs(w)<d.week)return{value:w,unit:"week"};const k=v.getFullYear()-_.getFullYear(),$=12*k+v.getMonth()-_.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<d.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const g={second:45,minute:45,hour:22,day:5,week:4,month:11};r()}catch(l){r(l)}}))},13965:function(e,t,a){a(26847),a(27530);var r=a(73742),o=a(59048),i=a(7616);let n,s,d,l=e=>e;class c extends o.oi{render(){return(0,o.dy)(n||(n=l`
      ${0}
      <slot></slot>
    `),this.header?(0,o.dy)(s||(s=l`<h1 class="card-header">${0}</h1>`),this.header):o.Ld)}constructor(...e){super(...e),this.raised=!1}}c.styles=(0,o.iv)(d||(d=l`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, 12px);
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: 12px 16px 16px;
      display: block;
      margin-block-start: 0px;
      margin-block-end: 0px;
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: 0px;
      margin-top: -8px;
    }

    :host ::slotted(.card-content) {
      padding: 16px;
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: 5px 16px;
    }
  `)),(0,r.__decorate)([(0,i.Cb)()],c.prototype,"header",void 0),(0,r.__decorate)([(0,i.Cb)({type:Boolean,reflect:!0})],c.prototype,"raised",void 0),c=(0,r.__decorate)([(0,i.Mo)("ha-card")],c)},83379:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:()=>f});a(26847),a(81738),a(6989),a(27530);var o=a(73742),i=a(59048),n=a(7616),s=a(31733),d=a(77204),l=(a(51431),a(78645),a(40830),a(27341)),c=(a(72633),a(1963),e([l]));l=(c.then?(await c)():c)[0];let p,h,u,g,b,v,_,m,y=e=>e;const x="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class f extends i.oi{render(){return(0,i.dy)(p||(p=y`
      ${0}
    `),this.narrow?(0,i.dy)(h||(h=y` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),x,this.items.map((e=>e.divider?(0,i.dy)(u||(u=y`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,i.dy)(g||(g=y`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item> `),e.disabled,e.action,(0,s.$)({warning:Boolean(e.warning)}),(0,s.$)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,i.dy)(b||(b=y`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?i.Ld:e.divider?(0,i.dy)(v||(v=y`<div role="separator"></div>`)):(0,i.dy)(_||(_=y`<ha-tooltip
                      .disabled=${0}
                      .content=${0}
                    >
                      <ha-icon-button
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button>
                    </ha-tooltip>`),!e.tooltip,null!==(t=e.tooltip)&&void 0!==t?t:"",e.action,e.label,e.path,e.disabled)}))))}_handleIconOverflowMenuOpened(e){e.stopPropagation()}static get styles(){return[d.Qx,(0,i.iv)(m||(m=y`
        :host {
          display: flex;
          justify-content: flex-end;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}constructor(...e){super(...e),this.items=[],this.narrow=!1}}(0,o.__decorate)([(0,n.Cb)({attribute:!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({type:Array})],f.prototype,"items",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean})],f.prototype,"narrow",void 0),f=(0,o.__decorate)([(0,n.Mo)("ha-icon-overflow-menu")],f),r()}catch(p){r(p)}}))},27341:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(73742),o=a(52634),i=a(62685),n=a(59048),s=a(7616),d=a(75535),l=e([o]);o=(l.then?(await l)():l)[0];let c,p=e=>e;(0,d.jx)("tooltip.show",{keyframes:[{opacity:0},{opacity:1}],options:{duration:150,easing:"ease"}}),(0,d.jx)("tooltip.hide",{keyframes:[{opacity:1},{opacity:0}],options:{duration:400,easing:"ease"}});class h extends o.Z{}h.styles=[i.Z,(0,n.iv)(c||(c=p`
      :host {
        --sl-tooltip-background-color: var(--secondary-background-color);
        --sl-tooltip-color: var(--primary-text-color);
        --sl-tooltip-font-family: var(
          --ha-tooltip-font-family,
          var(--ha-font-family-body)
        );
        --sl-tooltip-font-size: var(
          --ha-tooltip-font-size,
          var(--ha-font-size-s)
        );
        --sl-tooltip-font-weight: var(
          --ha-tooltip-font-weight,
          var(--ha-font-weight-normal)
        );
        --sl-tooltip-line-height: var(
          --ha-tooltip-line-height,
          var(--ha-line-height-condensed)
        );
        --sl-tooltip-padding: 8px;
        --sl-tooltip-border-radius: var(--ha-tooltip-border-radius, 4px);
        --sl-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
        --sl-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
      }
    `))],h=(0,r.__decorate)([(0,s.Mo)("ha-tooltip")],h),t()}catch(c){t(c)}}))},15724:function(e,t,a){a.d(t,{q:()=>l});a(40777),a(39710),a(56389),a(26847),a(70820),a(64455),a(40005),a(27530);const r=/^[v^~<>=]*?(\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+)(?:\.([x*]|\d+))?(?:-([\da-z\-]+(?:\.[\da-z\-]+)*))?(?:\+[\da-z\-]+(?:\.[\da-z\-]+)*)?)?)?$/i,o=e=>{if("string"!=typeof e)throw new TypeError("Invalid argument expected string");const t=e.match(r);if(!t)throw new Error(`Invalid argument not valid semver ('${e}' received)`);return t.shift(),t},i=e=>"*"===e||"x"===e||"X"===e,n=e=>{const t=parseInt(e,10);return isNaN(t)?e:t},s=(e,t)=>{if(i(e)||i(t))return 0;const[a,r]=((e,t)=>typeof e!=typeof t?[String(e),String(t)]:[e,t])(n(e),n(t));return a>r?1:a<r?-1:0},d=(e,t)=>{for(let a=0;a<Math.max(e.length,t.length);a++){const r=s(e[a]||"0",t[a]||"0");if(0!==r)return r}return 0},l=(e,t,a)=>{h(a);const r=((e,t)=>{const a=o(e),r=o(t),i=a.pop(),n=r.pop(),s=d(a,r);return 0!==s?s:i&&n?d(i.split("."),n.split(".")):i||n?i?-1:1:0})(e,t);return c[a].includes(r)},c={">":[1],">=":[0,1],"=":[0],"<=":[-1,0],"<":[-1],"!=":[-1,1]},p=Object.keys(c),h=e=>{if("string"!=typeof e)throw new TypeError("Invalid operator type, expected string but got "+typeof e);if(-1===p.indexOf(e))throw new Error(`Invalid operator, expected one of ${p.join("|")}`)}},92799:function(e,t,a){a(26847),a(44438),a(81738),a(22960),a(6989),a(93190),a(27530);var r=a(73742),o=a(59048),i=a(7616),n=a(31733),s=a(29740),d=a(38059);let l,c,p,h,u,g,b=e=>e;const v=new d.r("knx-project-tree-view");class _ extends o.oi{connectedCallback(){super.connectedCallback();const e=t=>{Object.entries(t).forEach((([t,a])=>{a.group_addresses.length>0&&(this._selectableRanges[t]={selected:!1,groupAddresses:a.group_addresses}),e(a.group_ranges)}))};e(this.data.group_ranges),v.debug("ranges",this._selectableRanges)}render(){return(0,o.dy)(l||(l=b`<div class="ha-tree-view">${0}</div>`),this._recurseData(this.data.group_ranges))}_recurseData(e,t=0){const a=Object.entries(e).map((([e,a])=>{const r=Object.keys(a.group_ranges).length>0;if(!(r||a.group_addresses.length>0))return o.Ld;const i=e in this._selectableRanges,s=!!i&&this._selectableRanges[e].selected,d={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:i,"selected-range":s,"non-selected-range":i&&!s},l=(0,o.dy)(c||(c=b`<div
        class=${0}
        toggle-range=${0}
        @click=${0}
      >
        <span class="range-key">${0}</span>
        <span class="range-text">${0}</span>
      </div>`),(0,n.$)(d),i?e:o.Ld,i?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:o.Ld,e,a.name);if(r){const e={"root-group":0===t,"sub-group":0!==t};return(0,o.dy)(p||(p=b`<div class=${0}>
          ${0} ${0}
        </div>`),(0,n.$)(e),l,this._recurseData(a.group_ranges,t+1))}return(0,o.dy)(h||(h=b`${0}`),l)}));return(0,o.dy)(u||(u=b`${0}`),a)}_selectionChangedMulti(e){const t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}_selectionChangedSingle(e){const t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}_selectionUpdate(){const e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);v.debug("selection changed",e),(0,s.B)(this,"knx-group-range-selection-changed",{groupAddresses:e})}constructor(...e){super(...e),this.multiselect=!1,this._selectableRanges={}}}_.styles=(0,o.iv)(g||(g=b`
    :host {
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--card-background-color);
    }

    .ha-tree-view {
      cursor: default;
    }

    .root-group {
      margin-bottom: 8px;
    }

    .root-group > * {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .range-item {
      display: block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-size: 0.875rem;
    }

    .range-item > * {
      vertical-align: middle;
      pointer-events: none;
    }

    .range-key {
      color: var(--text-primary-color);
      font-size: 0.75rem;
      font-weight: 700;
      background-color: var(--label-badge-grey);
      border-radius: 4px;
      padding: 1px 4px;
      margin-right: 2px;
    }

    .root-range {
      padding-left: 8px;
      font-weight: 500;
      background-color: var(--secondary-background-color);

      & .range-key {
        color: var(--primary-text-color);
        background-color: var(--card-background-color);
      }
    }

    .sub-range {
      padding-left: 13px;
    }

    .selectable {
      cursor: pointer;
    }

    .selectable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    .selected-range {
      background-color: rgba(var(--rgb-primary-color), 0.12);

      & .range-key {
        background-color: var(--primary-color);
      }
    }

    .selected-range:hover {
      background-color: rgba(var(--rgb-primary-color), 0.07);
    }

    .non-selected-range {
      background-color: var(--card-background-color);
    }
  `)),(0,r.__decorate)([(0,i.Cb)({attribute:!1})],_.prototype,"data",void 0),(0,r.__decorate)([(0,i.Cb)({attribute:!1})],_.prototype,"multiselect",void 0),(0,r.__decorate)([(0,i.SB)()],_.prototype,"_selectableRanges",void 0),_=(0,r.__decorate)([(0,i.Mo)("knx-project-tree-view")],_)},65793:function(e,t,a){a.d(t,{Am:()=>d,Wl:()=>i,Yh:()=>n,f3:()=>o,q$:()=>s,xi:()=>l});a(44438),a(81738),a(93190),a(64455),a(56303),a(40005);var r=a(24110);const o={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,r.$w)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=o.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},i=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),n=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),d=e=>{const t=new Date(e),a=e.match(/\.(\d{6})/),r=a?a[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+r},l=e=>`${e.getUTCMinutes().toString().padStart(2,"0")}:${e.getUTCSeconds().toString().padStart(2,"0")}.${e.getUTCMilliseconds().toString().padStart(3,"0")}`},18988:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:()=>T});a(39710),a(26847),a(2394),a(44438),a(81738),a(93190),a(87799),a(1455),a(56303),a(56389),a(27530);var o=a(73742),i=a(59048),n=a(7616),s=a(28105),d=a(29173),l=a(86829),c=(a(62790),a(13965),a(78645),a(83379)),p=(a(32780),a(60495)),h=(a(92799),a(15724)),u=a(63279),g=a(38059),b=a(65793),v=e([l,c,p]);[l,c,p]=v.then?(await v)():v;let _,m,y,x,f,w,k,$,j,S,M,A,C=e=>e;const z="M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",H="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",R="M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",V=new g.r("knx-project-view"),O="3.3.0";class T extends i.oi{disconnectedCallback(){super.disconnectedCallback(),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}async firstUpdated(){this.knx.project?this._isGroupRangeAvailable():this.knx.loadProject().then((()=>{this._isGroupRangeAvailable(),this.requestUpdate()})),(0,u.ze)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{V.error("getGroupTelegrams",e),(0,d.c)("/knx/error",{replace:!0,data:e})})),this._subscribed=await(0,u.IP)(this.hass,(e=>{this.telegram_callback(e)}))}_isGroupRangeAvailable(){var e,t;const a=null!==(e=null===(t=this.knx.project)||void 0===t?void 0:t.knxproject.info.xknxproject_version)&&void 0!==e?e:"0.0.0";V.debug("project version: "+a),this._groupRangeAvailable=(0,h.q)(a,O,">=")}telegram_callback(e){this._lastTelegrams=Object.assign(Object.assign({},this._lastTelegrams),{},{[e.destination]:e})}_groupAddressMenu(e){var t;const a=[];return a.push({path:R,label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,d.c)(`/knx/group_monitor?destination=${e.address}`)}}),1===(null===(t=e.dpt)||void 0===t?void 0:t.main)&&a.push({path:H,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,d.c)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}}),(0,i.dy)(_||(_=C`
      <ha-icon-overflow-menu .hass=${0} narrow .items=${0}> </ha-icon-overflow-menu>
    `),this.hass,a)}_getRows(e){return e.length?Object.entries(this.knx.project.knxproject.group_addresses).reduce(((t,[a,r])=>(e.includes(a)&&t.push(r),t)),[]):Object.values(this.knx.project.knxproject.group_addresses)}_visibleAddressesChanged(e){this._visibleGroupAddresses=e.detail.groupAddresses}render(){if(!this.hass||!this.knx.project)return(0,i.dy)(m||(m=C` <hass-loading-screen></hass-loading-screen> `));const e=this._getRows(this._visibleGroupAddresses);return(0,i.dy)(y||(y=C`
      <hass-tabs-subpage
        .hass=${0}
        .narrow=${0}
        .route=${0}
        .tabs=${0}
        .localizeFunc=${0}
      >
        ${0}
      </hass-tabs-subpage>
    `),this.hass,this.narrow,this.route,this.tabs,this.knx.localize,this.knx.project.project_loaded?(0,i.dy)(x||(x=C`${0}
              <div class="sections">
                ${0}
                <ha-data-table
                  class="ga-table"
                  .hass=${0}
                  .columns=${0}
                  .data=${0}
                  .hasFab=${0}
                  .searchLabel=${0}
                  .clickable=${0}
                ></ha-data-table>
              </div>`),this.narrow&&this._groupRangeAvailable?(0,i.dy)(f||(f=C`<ha-icon-button
                    slot="toolbar-icon"
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),this.hass.localize("ui.components.related-filter-menu.filter"),z,this._toggleRangeSelector):i.Ld,this._groupRangeAvailable?(0,i.dy)(w||(w=C`
                      <knx-project-tree-view
                        .data=${0}
                        @knx-group-range-selection-changed=${0}
                      ></knx-project-tree-view>
                    `),this.knx.project.knxproject,this._visibleAddressesChanged):i.Ld,this.hass,this._columns(this.narrow,this.hass.language),e,!1,this.hass.localize("ui.components.data-table.search"),!1):(0,i.dy)(k||(k=C` <ha-card .header=${0}>
              <div class="card-content">
                <p>${0}</p>
              </div>
            </ha-card>`),this.knx.localize("attention"),this.knx.localize("project_view_upload")))}_toggleRangeSelector(){this.rangeSelectorHidden=!this.rangeSelectorHidden}constructor(...e){super(...e),this.rangeSelectorHidden=!0,this._visibleGroupAddresses=[],this._groupRangeAvailable=!1,this._lastTelegrams={},this._columns=(0,s.Z)(((e,t)=>({address:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_address"),flex:1,minWidth:"100px"},name:{filterable:!0,sortable:!0,title:this.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:this.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?(0,i.dy)($||($=C`<span style="display:inline-block;width:24px;text-align:right;"
                  >${0}</span
                >${0} `),e.dpt.main,e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""):""},lastValue:{filterable:!0,title:this.knx.localize("project_view_table_last_value"),flex:2,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=b.f3.payload(t);return null==t.value?(0,i.dy)(j||(j=C`<code>${0}</code>`),a):(0,i.dy)(S||(S=C`<div title=${0}>
            ${0}
          </div>`),a,b.f3.valueWithUnit(this._lastTelegrams[e.address]))}},updated:{title:this.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:e=>{const t=this._lastTelegrams[e.address];if(!t)return"";const a=`${b.f3.dateWithMilliseconds(t)}\n\n${t.source} ${t.source_name}`;return(0,i.dy)(M||(M=C`<div title=${0}>
            ${0}
          </div>`),a,(0,p.G)(new Date(t.timestamp),this.hass.locale))}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:e=>this._groupAddressMenu(e)}})))}}T.styles=(0,i.iv)(A||(A=C`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
    .sections {
      display: flex;
      flex-direction: row;
      height: 100%;
    }

    :host([narrow]) knx-project-tree-view {
      position: absolute;
      max-width: calc(100% - 60px); /* 100% -> max 871px before not narrow */
      z-index: 1;
      right: 0;
      transition: 0.5s;
      border-left: 1px solid var(--divider-color);
    }

    :host([narrow][range-selector-hidden]) knx-project-tree-view {
      width: 0;
    }

    :host(:not([narrow])) knx-project-tree-view {
      max-width: 255px; /* min 616px - 816px for tree-view + ga-table (depending on side menu) */
    }

    .ga-table {
      flex: 1;
    }
  `)),(0,o.__decorate)([(0,n.Cb)({type:Object})],T.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],T.prototype,"knx",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0})],T.prototype,"narrow",void 0),(0,o.__decorate)([(0,n.Cb)({type:Object})],T.prototype,"route",void 0),(0,o.__decorate)([(0,n.Cb)({type:Array,reflect:!1})],T.prototype,"tabs",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],T.prototype,"rangeSelectorHidden",void 0),(0,o.__decorate)([(0,n.SB)()],T.prototype,"_visibleGroupAddresses",void 0),(0,o.__decorate)([(0,n.SB)()],T.prototype,"_groupRangeAvailable",void 0),(0,o.__decorate)([(0,n.SB)()],T.prototype,"_subscribed",void 0),(0,o.__decorate)([(0,n.SB)()],T.prototype,"_lastTelegrams",void 0),T=(0,o.__decorate)([(0,n.Mo)("knx-project-view")],T),r()}catch(_){r(_)}}))}}]);
//# sourceMappingURL=2669.4a6dbda7134be7b5.js.map