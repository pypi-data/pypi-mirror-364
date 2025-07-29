"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["133"],{85163:function(t,e,i){i.d(e,{wZ:()=>n,jL:()=>o});i(26847),i(81738),i(94814),i(6989),i(20655),i(27530);var s=i(28105),a=i(31298);i(67886),i(65451),i(46015),i(38334),i(94880),i(75643),i(29761);const o=t=>{var e;return null===(e=t.name_by_user||t.name)||void 0===e?void 0:e.trim()},n=(t,e,i)=>o(t)||i&&r(e,i)||e.localize("ui.panel.config.devices.unnamed_device",{type:e.localize(`ui.panel.config.devices.type.${t.entry_type||"device"}`)}),r=(t,e)=>{for(const i of e||[]){const e="string"==typeof i?i:i.entity_id,s=t.states[e];if(s)return(0,a.C)(s)}};(0,s.Z)((t=>function(t){const e=new Set,i=new Set;for(const s of t)i.has(s)?e.add(s):i.add(s);return e}(Object.values(t).map((t=>o(t))).filter((t=>void 0!==t)))))},10996:function(t,e,i){i.d(e,{K:()=>r});var s=i(85163),a=i(31298);i(26847),i(44261),i(27530);const o=[" ",": "," - "],n=t=>t.toLowerCase()!==t,r=(t,e)=>{const i=e.entities[t.entity_id];return i?d(i,e):(0,a.C)(t)},d=(t,e)=>{const i=t.name||("original_name"in t?t.original_name:void 0),r=t.device_id?e.devices[t.device_id]:void 0;if(!r){if(i)return i;const s=e.states[t.entity_id];return s?(0,a.C)(s):void 0}const d=(0,s.jL)(r);if(d!==i)return d&&i&&((t,e)=>{const i=t.toLowerCase(),s=e.toLowerCase();for(const a of o){const e=`${s}${a}`;if(i.startsWith(e)){const i=t.substring(e.length);if(i.length)return n(i.substr(0,i.indexOf(" ")))?i:i[0].toUpperCase()+i.slice(1)}}})(i,d)||i}},66027:function(t,e,i){i.d(e,{getEntityContext:()=>s});const s=(t,e)=>{const i=e.entities[t.entity_id];return i?a(i,e):{entity:null,device:null,area:null,floor:null}},a=(t,e)=>{const i=e.entities[t.entity_id],s=null==t?void 0:t.device_id,a=s?e.devices[s]:void 0,o=(null==t?void 0:t.area_id)||(null==a?void 0:a.area_id),n=o?e.areas[o]:void 0,r=null==n?void 0:n.floor_id;return{entity:i,device:a||null,area:n||null,floor:(r?e.floors[r]:void 0)||null}}},27087:function(t,e,i){i.d(e,{T:()=>a});i(64455),i(32192);const s=/^(\w+)\.(\w+)$/,a=t=>s.test(t)},39711:function(t,e,i){i.a(t,(async function(t,e){try{i(39710),i(26847),i(73042),i(81738),i(94814),i(6989),i(1455),i(56389),i(44261),i(27530);var s=i(73742),a=i(59048),o=i(7616),n=i(28105),r=i(29740),d=i(71188),l=i(85163),c=i(76151),u=i(10996),h=i(31298),p=i(66027),_=i(27087),y=i(80913),v=i(47469),b=i(56845),m=i(37596),f=(i(57264),i(33321)),g=(i(40830),i(37351)),C=t([f,g]);[f,g]=C.then?(await C)():C;let $,w,j,O,I,x,k,E,L,B=t=>t;const V="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",D="M11,13.5V21.5H3V13.5H11M12,2L17.5,11H6.5L12,2M17.5,13C20,13 22,15 22,17.5C22,20 20,22 17.5,22C15,22 13,20 13,17.5C13,15 15,13 17.5,13Z",H="___create-new-entity___";class A extends a.oi{firstUpdated(t){super.firstUpdated(t),this.hass.loadBackendTranslation("title")}get _showEntityId(){var t;return this.showEntityId||(null===(t=this.hass.userData)||void 0===t?void 0:t.showEntityIdPicker)}render(){var t;const e=null!==(t=this.placeholder)&&void 0!==t?t:this.hass.localize("ui.components.entity.entity-picker.placeholder"),i=this.hass.localize("ui.components.entity.entity-picker.no_match");return(0,a.dy)($||($=B`
      <ha-generic-picker
        .hass=${0}
        .disabled=${0}
        .autofocus=${0}
        .allowCustomValue=${0}
        .label=${0}
        .helper=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .getAdditionalItems=${0}
        .hideClearIcon=${0}
        .searchFn=${0}
        .valueRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.disabled,this.autofocus,this.allowCustomEntity,this.label,this.helper,this.searchLabel,i,e,this.value,this._rowRenderer,this._getItems,this._getAdditionalItems,this.hideClearIcon,this._searchFn,this._valueRenderer,this._valueChanged)}async open(){var t;await this.updateComplete,await(null===(t=this._picker)||void 0===t?void 0:t.open())}_valueChanged(t){t.stopPropagation();const e=t.detail.value;if(e)if(e.startsWith(H)){const t=e.substring(H.length);(0,m.j)(this,{domain:t,dialogClosedCallback:t=>{t.entityId&&this._setValue(t.entityId)}})}else(0,_.T)(e)&&this._setValue(e);else this._setValue(void 0)}_setValue(t){this.value=t,(0,r.B)(this,"value-changed",{value:t}),(0,r.B)(this,"change")}constructor(...t){super(...t),this.autofocus=!1,this.disabled=!1,this.required=!1,this.showEntityId=!1,this.hideClearIcon=!1,this._valueRenderer=t=>{const e=t||"",i=this.hass.states[e];if(!i)return(0,a.dy)(w||(w=B`
        <ha-svg-icon
          slot="start"
          .path=${0}
          style="margin: 0 4px"
        ></ha-svg-icon>
        <span slot="headline">${0}</span>
      `),D,e);const{area:s,device:o}=(0,p.getEntityContext)(i,this.hass),n=(0,u.K)(i,this.hass),r=o?(0,l.jL)(o):void 0,c=s?(0,d.D)(s):void 0,h=(0,y.HE)(this.hass),_=n||r||e,v=[c,n?r:void 0].filter(Boolean).join(h?" ◂ ":" ▸ ");return(0,a.dy)(j||(j=B`
      <state-badge
        .hass=${0}
        .stateObj=${0}
        slot="start"
      ></state-badge>
      <span slot="headline">${0}</span>
      <span slot="supporting-text">${0}</span>
    `),this.hass,i,_,v)},this._rowRenderer=(t,{index:e})=>{const i=this._showEntityId;return(0,a.dy)(O||(O=B`
      <ha-combo-box-item type="button" compact .borderTop=${0}>
        ${0}
        <span slot="headline">${0}</span>
        ${0}
        ${0}
        ${0}
      </ha-combo-box-item>
    `),0!==e,t.icon_path?(0,a.dy)(I||(I=B`
              <ha-svg-icon
                slot="start"
                style="margin: 0 4px"
                .path=${0}
              ></ha-svg-icon>
            `),t.icon_path):(0,a.dy)(x||(x=B`
              <state-badge
                slot="start"
                .stateObj=${0}
                .hass=${0}
              ></state-badge>
            `),t.stateObj,this.hass),t.primary,t.secondary?(0,a.dy)(k||(k=B`<span slot="supporting-text">${0}</span>`),t.secondary):a.Ld,t.stateObj&&i?(0,a.dy)(E||(E=B`
              <span slot="supporting-text" class="code">
                ${0}
              </span>
            `),t.stateObj.entity_id):a.Ld,t.domain_name&&!i?(0,a.dy)(L||(L=B`
              <div slot="trailing-supporting-text" class="domain">
                ${0}
              </div>
            `),t.domain_name):a.Ld)},this._getAdditionalItems=()=>this._getCreateItems(this.hass.localize,this.createDomains),this._getCreateItems=(0,n.Z)(((t,e)=>null!=e&&e.length?e.map((e=>{const i=t("ui.components.entity.entity-picker.create_helper",{domain:(0,b.X)(e)?t(`ui.panel.config.helpers.types.${e}`):(0,v.Lh)(t,e)});return{id:H+e,primary:i,secondary:t("ui.components.entity.entity-picker.new_entity"),icon_path:V}})):[])),this._getItems=()=>this._getEntities(this.hass,this.includeDomains,this.excludeDomains,this.entityFilter,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.includeEntities,this.excludeEntities),this._getEntities=(0,n.Z)(((t,e,i,s,a,o,n,r)=>{let _=[],b=Object.keys(t.states);n&&(b=b.filter((t=>n.includes(t)))),r&&(b=b.filter((t=>!r.includes(t)))),e&&(b=b.filter((t=>e.includes((0,c.M)(t))))),i&&(b=b.filter((t=>!i.includes((0,c.M)(t)))));const m=(0,y.HE)(this.hass);return _=b.map((e=>{const i=t.states[e],{area:s,device:a}=(0,p.getEntityContext)(i,t),o=(0,h.C)(i),n=(0,u.K)(i,t),r=a?(0,l.jL)(a):void 0,_=s?(0,d.D)(s):void 0,y=(0,v.Lh)(this.hass.localize,(0,c.M)(e)),b=n||r||e,f=[_,n?r:void 0].filter(Boolean).join(m?" ◂ ":" ▸ "),g=[r,n].filter(Boolean).join(" - ");return{id:e,primary:b,secondary:f,domain_name:y,sorting_label:[r,n].filter(Boolean).join("_"),search_labels:[n,r,_,y,o,e].filter(Boolean),a11y_label:g,stateObj:i}})),a&&(_=_.filter((t=>{var e;return t.id===this.value||(null===(e=t.stateObj)||void 0===e?void 0:e.attributes.device_class)&&a.includes(t.stateObj.attributes.device_class)}))),o&&(_=_.filter((t=>{var e;return t.id===this.value||(null===(e=t.stateObj)||void 0===e?void 0:e.attributes.unit_of_measurement)&&o.includes(t.stateObj.attributes.unit_of_measurement)}))),s&&(_=_.filter((t=>t.id===this.value||t.stateObj&&s(t.stateObj)))),_})),this._searchFn=(t,e)=>{const i=e.findIndex((e=>{var i;return(null===(i=e.stateObj)||void 0===i?void 0:i.entity_id)===t}));if(-1===i)return e;const[s]=e.splice(i,1);return e.unshift(s),e}}}(0,s.__decorate)([(0,o.Cb)({attribute:!1})],A.prototype,"hass",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],A.prototype,"autofocus",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],A.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],A.prototype,"required",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean,attribute:"allow-custom-entity"})],A.prototype,"allowCustomEntity",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean,attribute:"show-entity-id"})],A.prototype,"showEntityId",void 0),(0,s.__decorate)([(0,o.Cb)()],A.prototype,"label",void 0),(0,s.__decorate)([(0,o.Cb)()],A.prototype,"value",void 0),(0,s.__decorate)([(0,o.Cb)()],A.prototype,"helper",void 0),(0,s.__decorate)([(0,o.Cb)()],A.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.Cb)({type:String,attribute:"search-label"})],A.prototype,"searchLabel",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1,type:Array})],A.prototype,"createDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-domains"})],A.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-domains"})],A.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-device-classes"})],A.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-unit-of-measurement"})],A.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-entities"})],A.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-entities"})],A.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],A.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:"hide-clear-icon",type:Boolean})],A.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,o.IO)("ha-generic-picker")],A.prototype,"_picker",void 0),A=(0,s.__decorate)([(0,o.Mo)("ha-entity-picker")],A),e()}catch($){e($)}}))},39929:function(t,e,i){i.d(e,{iI:()=>a,oT:()=>s});i(39710),i(81738),i(6989),i(21700),i(87799),i(1455),i(26086),i(56389);const s=t=>t.map((t=>{if("string"!==t.type)return t;switch(t.name){case"username":return Object.assign(Object.assign({},t),{},{autocomplete:"username",autofocus:!0});case"password":return Object.assign(Object.assign({},t),{},{autocomplete:"current-password"});case"code":return Object.assign(Object.assign({},t),{},{autocomplete:"one-time-code",autofocus:!0});default:return t}})),a=(t,e)=>t.callWS({type:"auth/sign_path",path:e})},64930:function(t,e,i){i.d(e,{ON:()=>n,PX:()=>r,V_:()=>d,lz:()=>o,nZ:()=>a,rk:()=>c});var s=i(13228);const a="unavailable",o="unknown",n="on",r="off",d=[a,o],l=[a,o,r],c=(0,s.z)(d);(0,s.z)(l)},47469:function(t,e,i){i.d(e,{F3:()=>a,Lh:()=>s,t4:()=>o});i(16811);const s=(t,e,i)=>t(`component.${e}.title`)||(null==i?void 0:i.name)||e,a=(t,e)=>{const i={type:"manifest/list"};return e&&(i.integrations=e),t.callWS(i)},o=(t,e)=>t.callWS({type:"manifest/get",integration:e})},37596:function(t,e,i){i.d(e,{j:()=>o});i(26847),i(1455),i(27530);var s=i(29740);const a=()=>Promise.all([i.e("2092"),i.e("8745")]).then(i.bind(i,35030)),o=(t,e)=>{(0,s.B)(t,"show-dialog",{dialogTag:"dialog-helper-detail",dialogImport:a,dialogParams:e})}}}]);
//# sourceMappingURL=133.4705ae704846ac0d.js.map