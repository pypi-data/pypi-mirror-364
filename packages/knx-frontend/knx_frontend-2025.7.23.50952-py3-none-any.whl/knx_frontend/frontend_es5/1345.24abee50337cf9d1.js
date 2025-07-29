/*! For license information please see 1345.24abee50337cf9d1.js.LICENSE.txt */
"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1345"],{52245:function(e,t,i){i.a(e,(async function(e,t){try{i(39710),i(26847),i(81738),i(94814),i(6989),i(1455),i(56389),i(27530);var s=i(73742),r=i(59048),n=i(7616),a=i(28105),o=i(29740),l=i(27087),d=i(39711),c=e([d]);d=(c.then?(await c)():c)[0];let u,h,p,y,_=e=>e;class v extends r.oi{render(){if(!this.hass)return r.Ld;const e=this._currentEntities;return(0,r.dy)(u||(u=_`
      ${0}
      ${0}
      <div>
        <ha-entity-picker
          allow-custom-entity
          .hass=${0}
          .includeDomains=${0}
          .excludeDomains=${0}
          .includeEntities=${0}
          .excludeEntities=${0}
          .includeDeviceClasses=${0}
          .includeUnitOfMeasurement=${0}
          .entityFilter=${0}
          .placeholder=${0}
          .helper=${0}
          .disabled=${0}
          .createDomains=${0}
          .required=${0}
          @value-changed=${0}
        ></ha-entity-picker>
      </div>
    `),this.label?(0,r.dy)(h||(h=_`<label>${0}</label>`),this.label):r.Ld,e.map((e=>(0,r.dy)(p||(p=_`
          <div>
            <ha-entity-picker
              allow-custom-entity
              .curValue=${0}
              .hass=${0}
              .includeDomains=${0}
              .excludeDomains=${0}
              .includeEntities=${0}
              .excludeEntities=${0}
              .includeDeviceClasses=${0}
              .includeUnitOfMeasurement=${0}
              .entityFilter=${0}
              .value=${0}
              .disabled=${0}
              .createDomains=${0}
              @value-changed=${0}
            ></ha-entity-picker>
          </div>
        `),e,this.hass,this.includeDomains,this.excludeDomains,this.includeEntities,this.excludeEntities,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.entityFilter,e,this.disabled,this.createDomains,this._entityChanged))),this.hass,this.includeDomains,this.excludeDomains,this.includeEntities,this._excludeEntities(this.value,this.excludeEntities),this.includeDeviceClasses,this.includeUnitOfMeasurement,this.entityFilter,this.placeholder,this.helper,this.disabled,this.createDomains,this.required&&!e.length,this._addEntity)}get _currentEntities(){return this.value||[]}async _updateEntities(e){this.value=e,(0,o.B)(this,"value-changed",{value:e})}_entityChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;if(i===t||void 0!==i&&!(0,l.T)(i))return;const s=this._currentEntities;i&&!s.includes(i)?this._updateEntities(s.map((e=>e===t?i:e))):this._updateEntities(s.filter((e=>e!==t)))}async _addEntity(e){e.stopPropagation();const t=e.detail.value;if(!t)return;if(e.currentTarget.value="",!t)return;const i=this._currentEntities;i.includes(t)||this._updateEntities([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._excludeEntities=(0,a.Z)(((e,t)=>void 0===e?t:[...t||[],...e]))}}v.styles=(0,r.iv)(y||(y=_`
    div {
      margin-top: 8px;
    }
    label {
      display: block;
      margin: 0 0 8px;
    }
  `)),(0,s.__decorate)([(0,n.Cb)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array})],v.prototype,"value",void 0),(0,s.__decorate)([(0,n.Cb)({type:Boolean})],v.prototype,"disabled",void 0),(0,s.__decorate)([(0,n.Cb)({type:Boolean})],v.prototype,"required",void 0),(0,s.__decorate)([(0,n.Cb)()],v.prototype,"label",void 0),(0,s.__decorate)([(0,n.Cb)()],v.prototype,"placeholder",void 0),(0,s.__decorate)([(0,n.Cb)()],v.prototype,"helper",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-domains"})],v.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"exclude-domains"})],v.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-device-classes"})],v.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-unit-of-measurement"})],v.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"include-entities"})],v.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,n.Cb)({type:Array,attribute:"exclude-entities"})],v.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,n.Cb)({attribute:!1})],v.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,n.Cb)({attribute:!1,type:Array})],v.prototype,"createDomains",void 0),v=(0,s.__decorate)([(0,n.Mo)("ha-entities-picker")],v),t()}catch(u){t(u)}}))},87393:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaEntitySelector:()=>$});i(26847),i(81738),i(94814),i(72489),i(27530);var r=i(73742),n=i(59048),a=i(7616),o=i(74608),l=i(29740),d=i(71170),c=i(45103),u=i(52245),h=i(39711),p=e([u,h]);[u,h]=p.then?(await p)():p;let y,_,v=e=>e;class $ extends n.oi{_hasIntegration(e){var t;return(null===(t=e.entity)||void 0===t?void 0:t.filter)&&(0,o.r)(e.entity.filter).some((e=>e.integration))}willUpdate(e){var t,i;e.has("selector")&&void 0!==this.value&&(null!==(t=this.selector.entity)&&void 0!==t&&t.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,l.B)(this,"value-changed",{value:this.value})):null!==(i=this.selector.entity)&&void 0!==i&&i.multiple||!Array.isArray(this.value)||(this.value=this.value[0],(0,l.B)(this,"value-changed",{value:this.value})))}render(){var e,t,i;return this._hasIntegration(this.selector)&&!this._entitySources?n.Ld:null!==(e=this.selector.entity)&&void 0!==e&&e.multiple?(0,n.dy)(_||(_=v`
      <ha-entities-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .includeEntities=${0}
        .excludeEntities=${0}
        .entityFilter=${0}
        .createDomains=${0}
        .disabled=${0}
        .required=${0}
      ></ha-entities-picker>
    `),this.hass,this.value,this.label,this.helper,this.selector.entity.include_entities,this.selector.entity.exclude_entities,this._filterEntities,this._createDomains,this.disabled,this.required):(0,n.dy)(y||(y=v`<ha-entity-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .includeEntities=${0}
        .excludeEntities=${0}
        .entityFilter=${0}
        .createDomains=${0}
        .disabled=${0}
        .required=${0}
        allow-custom-entity
      ></ha-entity-picker>`),this.hass,this.value,this.label,this.helper,null===(t=this.selector.entity)||void 0===t?void 0:t.include_entities,null===(i=this.selector.entity)||void 0===i?void 0:i.exclude_entities,this._filterEntities,this._createDomains,this.disabled,this.required)}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,d.m)(this.hass).then((e=>{this._entitySources=e})),e.has("selector")&&(this._createDomains=(0,c.bq)(this.selector))}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._filterEntities=e=>{var t;return null===(t=this.selector)||void 0===t||null===(t=t.entity)||void 0===t||!t.filter||(0,o.r)(this.selector.entity.filter).some((t=>(0,c.lV)(t,e,this._entitySources)))}}}(0,r.__decorate)([(0,a.Cb)({attribute:!1})],$.prototype,"hass",void 0),(0,r.__decorate)([(0,a.Cb)({attribute:!1})],$.prototype,"selector",void 0),(0,r.__decorate)([(0,a.SB)()],$.prototype,"_entitySources",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"value",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"label",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"helper",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],$.prototype,"disabled",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],$.prototype,"required",void 0),(0,r.__decorate)([(0,a.SB)()],$.prototype,"_createDomains",void 0),$=(0,r.__decorate)([(0,a.Mo)("ha-selector-entity")],$),s()}catch(y){s(y)}}))},71170:function(e,t,i){i.d(t,{m:()=>n});i(26847),i(1455),i(27530);const s=async(e,t,i,r,n,...a)=>{const o=n,l=o[e],d=l=>r&&r(n,l.result)!==l.cacheKey?(o[e]=void 0,s(e,t,i,r,n,...a)):l.result;if(l)return l instanceof Promise?l.then(d):d(l);const c=i(n,...a);return o[e]=c,c.then((i=>{o[e]={result:i,cacheKey:null==r?void 0:r(n,i)},setTimeout((()=>{o[e]=void 0}),t)}),(()=>{o[e]=void 0})),c},r=e=>e.callWS({type:"entity/source"}),n=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},28177:function(e,t,i){i.d(t,{C:()=>h});i(26847),i(81738),i(29981),i(1455),i(27530);var s=i(35340),r=i(5277),n=i(93847);i(84730),i(15411),i(40777);class a{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class o{get(){return this.Y}pause(){var e;null!==(e=this.Y)&&void 0!==e||(this.Y=new Promise((e=>this.Z=e)))}resume(){var e;null!==(e=this.Z)&&void 0!==e&&e.call(this),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var l=i(83522);const d=e=>!(0,r.pt)(e)&&"function"==typeof e.then,c=1073741823;class u extends n.sR{render(...e){var t;return null!==(t=e.find((e=>!d(e))))&&void 0!==t?t:s.Jb}update(e,t){const i=this._$Cbt;let r=i.length;this._$Cbt=t;const n=this._$CK,a=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<t.length&&!(s>this._$Cwt);s++){const e=t[s];if(!d(e))return this._$Cwt=s,e;s<r&&e===i[s]||(this._$Cwt=c,r=0,Promise.resolve(e).then((async t=>{for(;a.get();)await a.get();const i=n.deref();if(void 0!==i){const s=i._$Cbt.indexOf(e);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(t))}})))}return s.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new a(this),this._$CX=new o}}const h=(0,l.XM)(u)}}]);
//# sourceMappingURL=1345.24abee50337cf9d1.js.map