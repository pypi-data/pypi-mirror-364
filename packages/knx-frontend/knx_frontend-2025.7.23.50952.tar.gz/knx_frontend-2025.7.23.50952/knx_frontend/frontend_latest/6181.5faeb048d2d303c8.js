/*! For license information please see 6181.5faeb048d2d303c8.js.LICENSE.txt */
export const __webpack_ids__=["6181"];export const __webpack_modules__={13539:function(e,t,i){i.d(t,{Bt:()=>n});var o=i(3574),r=i(1066);const a=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"],n=e=>e.first_weekday===r.FS.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,o.L)(e.language)%7:a.includes(e.first_weekday)?a.indexOf(e.first_weekday):1},60495:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{G:()=>d});var r=i(57900),a=i(28105),n=i(58713),s=e([r,n]);[r,n]=s.then?(await s)():s;const l=(0,a.Z)((e=>new Intl.RelativeTimeFormat(e.language,{numeric:"auto"}))),d=(e,t,i,o=!0)=>{const r=(0,n.W)(e,i,t);return o?l(t).format(r.value,r.unit):Intl.NumberFormat(t.language,{style:"unit",unit:r.unit,unitDisplay:"long"}).format(Math.abs(r.value))};o()}catch(l){o(l)}}))},31132:function(e,t,i){i.d(t,{f:()=>o});const o=e=>e.charAt(0).toUpperCase()+e.slice(1)},58713:function(e,t,i){i.a(e,(async function(e,o){try{i.d(t,{W:()=>p});var r=i(7722),a=i(66233),n=i(41238),s=i(13539);const d=1e3,c=60,h=60*c;function p(e,t=Date.now(),i,o={}){const l={...u,...o||{}},p=(+e-+t)/d;if(Math.abs(p)<l.second)return{value:Math.round(p),unit:"second"};const g=p/c;if(Math.abs(g)<l.minute)return{value:Math.round(g),unit:"minute"};const m=p/h;if(Math.abs(m)<l.hour)return{value:Math.round(m),unit:"hour"};const _=new Date(e),x=new Date(t);_.setHours(0,0,0,0),x.setHours(0,0,0,0);const f=(0,r.j)(_,x);if(0===f)return{value:Math.round(m),unit:"hour"};if(Math.abs(f)<l.day)return{value:f,unit:"day"};const b=(0,s.Bt)(i),v=(0,a.z)(_,{weekStartsOn:b}),y=(0,a.z)(x,{weekStartsOn:b}),w=(0,n.p)(v,y);if(0===w)return{value:f,unit:"day"};if(Math.abs(w)<l.week)return{value:w,unit:"week"};const k=_.getFullYear()-x.getFullYear(),$=12*k+_.getMonth()-x.getMonth();return 0===$?{value:w,unit:"week"}:Math.abs($)<l.month||0===k?{value:$,unit:"month"}:{value:Math.round(k),unit:"year"}}const u={second:45,minute:45,hour:22,day:5,week:4,month:11};o()}catch(l){o(l)}}))},22543:function(e,t,i){i.r(t);var o=i(73742),r=i(59048),a=i(7616),n=i(31733),s=i(29740);i(78645),i(40830);const l={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class d extends r.oi{render(){return r.dy`
      <div
        class="issue-type ${(0,n.$)({[this.alertType]:!0})}"
        role="alert"
      >
        <div class="icon ${this.title?"":"no-title"}">
          <slot name="icon">
            <ha-svg-icon .path=${l[this.alertType]}></ha-svg-icon>
          </slot>
        </div>
        <div class=${(0,n.$)({content:!0,narrow:this.narrow})}>
          <div class="main-content">
            ${this.title?r.dy`<div class="title">${this.title}</div>`:r.Ld}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${this.dismissable?r.dy`<ha-icon-button
                    @click=${this._dismissClicked}
                    label="Dismiss alert"
                    .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                  ></ha-icon-button>`:r.Ld}
            </slot>
          </div>
        </div>
      </div>
    `}_dismissClicked(){(0,s.B)(this,"alert-dismissed-clicked")}constructor(...e){super(...e),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}d.styles=r.iv`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: 4px;
    }
    .icon {
      z-index: 1;
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 0;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action mwc-button,
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `,(0,o.__decorate)([(0,a.Cb)()],d.prototype,"title",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"alert-type"})],d.prototype,"alertType",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],d.prototype,"dismissable",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],d.prototype,"narrow",void 0),d=(0,o.__decorate)([(0,a.Mo)("ha-alert")],d)},99298:function(e,t,i){i.d(t,{i:()=>d});var o=i(73742),r=i(24004),a=i(75907),n=i(59048),s=i(7616);i(90380),i(78645);const l=["button","ha-list-item"],d=(e,t)=>n.dy`
  <div class="header_title">
    <ha-icon-button
      .label=${e?.localize("ui.common.close")??"Close"}
      .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
      dialogAction="close"
      class="header_button"
    ></ha-icon-button>
    <span>${t}</span>
  </div>
`;class c extends r.M{scrollToPos(e,t){this.contentElement?.scrollTo(e,t)}renderHeading(){return n.dy`<slot name="heading"> ${super.renderHeading()} </slot>`}firstUpdated(){super.firstUpdated(),this.suppressDefaultPressSelector=[this.suppressDefaultPressSelector,l].join(", "),this._updateScrolledAttribute(),this.contentElement?.addEventListener("scroll",this._onScroll,{passive:!0})}disconnectedCallback(){super.disconnectedCallback(),this.contentElement.removeEventListener("scroll",this._onScroll)}_updateScrolledAttribute(){this.contentElement&&this.toggleAttribute("scrolled",0!==this.contentElement.scrollTop)}constructor(...e){super(...e),this._onScroll=()=>{this._updateScrolledAttribute()}}}c.styles=[a.W,n.iv`
      :host([scrolled]) ::slotted(ha-dialog-header) {
        border-bottom: 1px solid
          var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
      }
      .mdc-dialog {
        --mdc-dialog-scroll-divider-color: var(
          --dialog-scroll-divider-color,
          var(--divider-color)
        );
        z-index: var(--dialog-z-index, 8);
        -webkit-backdrop-filter: var(
          --ha-dialog-scrim-backdrop-filter,
          var(--dialog-backdrop-filter, none)
        );
        backdrop-filter: var(
          --ha-dialog-scrim-backdrop-filter,
          var(--dialog-backdrop-filter, none)
        );
        --mdc-dialog-box-shadow: var(--dialog-box-shadow, none);
        --mdc-typography-headline6-font-weight: var(--ha-font-weight-normal);
        --mdc-typography-headline6-font-size: 1.574rem;
      }
      .mdc-dialog__actions {
        justify-content: var(--justify-action-buttons, flex-end);
        padding: 12px 24px max(var(--safe-area-inset-bottom), 12px) 24px;
      }
      .mdc-dialog__actions span:nth-child(1) {
        flex: var(--secondary-action-button-flex, unset);
      }
      .mdc-dialog__actions span:nth-child(2) {
        flex: var(--primary-action-button-flex, unset);
      }
      .mdc-dialog__container {
        align-items: var(--vertical-align-dialog, center);
      }
      .mdc-dialog__title {
        padding: 24px 24px 0 24px;
      }
      .mdc-dialog__title:has(span) {
        padding: 12px 12px 0;
      }
      .mdc-dialog__title::before {
        content: unset;
      }
      .mdc-dialog .mdc-dialog__content {
        position: var(--dialog-content-position, relative);
        padding: var(--dialog-content-padding, 24px);
      }
      :host([hideactions]) .mdc-dialog .mdc-dialog__content {
        padding-bottom: max(
          var(--dialog-content-padding, 24px),
          var(--safe-area-inset-bottom)
        );
      }
      .mdc-dialog .mdc-dialog__surface {
        position: var(--dialog-surface-position, relative);
        top: var(--dialog-surface-top);
        margin-top: var(--dialog-surface-margin-top);
        min-height: var(--mdc-dialog-min-height, auto);
        border-radius: var(--ha-dialog-border-radius, 28px);
        -webkit-backdrop-filter: var(--ha-dialog-surface-backdrop-filter, none);
        backdrop-filter: var(--ha-dialog-surface-backdrop-filter, none);
        background: var(
          --ha-dialog-surface-background,
          var(--mdc-theme-surface, #fff)
        );
      }
      :host([flexContent]) .mdc-dialog .mdc-dialog__content {
        display: flex;
        flex-direction: column;
      }
      .header_title {
        display: flex;
        align-items: center;
        direction: var(--direction);
      }
      .header_title span {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        display: block;
        padding-left: 4px;
      }
      .header_button {
        text-decoration: none;
        color: inherit;
        inset-inline-start: initial;
        inset-inline-end: -12px;
        direction: var(--direction);
      }
      .dialog-actions {
        inset-inline-start: initial !important;
        inset-inline-end: 0px !important;
        direction: var(--direction);
      }
    `],c=(0,o.__decorate)([(0,s.Mo)("ha-dialog")],c)},86932:function(e,t,i){i.d(t,{G:()=>d});var o=i(73742),r=i(59048),a=i(7616),n=i(31733),s=i(29740),l=i(98012);i(40830);class d extends r.oi{render(){const e=this.noCollapse?r.Ld:r.dy`
          <ha-svg-icon
            .path=${"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"}
            class="summary-icon ${(0,n.$)({expanded:this.expanded})}"
          ></ha-svg-icon>
        `;return r.dy`
      <div class="top ${(0,n.$)({expanded:this.expanded})}">
        <div
          id="summary"
          class=${(0,n.$)({noCollapse:this.noCollapse})}
          @click=${this._toggleContainer}
          @keydown=${this._toggleContainer}
          @focus=${this._focusChanged}
          @blur=${this._focusChanged}
          role="button"
          tabindex=${this.noCollapse?-1:0}
          aria-expanded=${this.expanded}
          aria-controls="sect1"
        >
          ${this.leftChevron?e:r.Ld}
          <slot name="leading-icon"></slot>
          <slot name="header">
            <div class="header">
              ${this.header}
              <slot class="secondary" name="secondary">${this.secondary}</slot>
            </div>
          </slot>
          ${this.leftChevron?r.Ld:e}
          <slot name="icons"></slot>
        </div>
      </div>
      <div
        class="container ${(0,n.$)({expanded:this.expanded})}"
        @transitionend=${this._handleTransitionEnd}
        role="region"
        aria-labelledby="summary"
        aria-hidden=${!this.expanded}
        tabindex="-1"
      >
        ${this._showContent?r.dy`<slot></slot>`:""}
      </div>
    `}willUpdate(e){super.willUpdate(e),e.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}_handleTransitionEnd(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}async _toggleContainer(e){if(e.defaultPrevented)return;if("keydown"===e.type&&"Enter"!==e.key&&" "!==e.key)return;if(e.preventDefault(),this.noCollapse)return;const t=!this.expanded;(0,s.B)(this,"expanded-will-change",{expanded:t}),this._container.style.overflow="hidden",t&&(this._showContent=!0,await(0,l.y)());const i=this._container.scrollHeight;this._container.style.height=`${i}px`,t||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=t,(0,s.B)(this,"expanded-changed",{expanded:this.expanded})}_focusChanged(e){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===e.type)}constructor(...e){super(...e),this.expanded=!1,this.outlined=!1,this.leftChevron=!1,this.noCollapse=!1,this._showContent=this.expanded}}d.styles=r.iv`
    :host {
      display: block;
    }

    .top {
      display: flex;
      align-items: center;
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .top.expanded {
      border-bottom-left-radius: 0px;
      border-bottom-right-radius: 0px;
    }

    .top.focused {
      background: var(--input-fill-color);
    }

    :host([outlined]) {
      box-shadow: none;
      border-width: 1px;
      border-style: solid;
      border-color: var(--outline-color);
      border-radius: var(--ha-card-border-radius, 12px);
    }

    .summary-icon {
      transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
      direction: var(--direction);
      margin-left: 8px;
      margin-inline-start: 8px;
      margin-inline-end: initial;
    }

    :host([left-chevron]) .summary-icon,
    ::slotted([slot="leading-icon"]) {
      margin-left: 0;
      margin-right: 8px;
      margin-inline-start: 0;
      margin-inline-end: 8px;
    }

    #summary {
      flex: 1;
      display: flex;
      padding: var(--expansion-panel-summary-padding, 0 8px);
      min-height: 48px;
      align-items: center;
      cursor: pointer;
      overflow: hidden;
      font-weight: var(--ha-font-weight-medium);
      outline: none;
    }
    #summary.noCollapse {
      cursor: default;
    }

    .summary-icon.expanded {
      transform: rotate(180deg);
    }

    .header,
    ::slotted([slot="header"]) {
      flex: 1;
      overflow-wrap: anywhere;
    }

    .container {
      padding: var(--expansion-panel-content-padding, 0 8px);
      overflow: hidden;
      transition: height 300ms cubic-bezier(0.4, 0, 0.2, 1);
      height: 0px;
    }

    .container.expanded {
      height: auto;
    }

    .secondary {
      display: block;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
  `,(0,o.__decorate)([(0,a.Cb)({type:Boolean,reflect:!0})],d.prototype,"expanded",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean,reflect:!0})],d.prototype,"outlined",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"left-chevron",type:Boolean,reflect:!0})],d.prototype,"leftChevron",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"no-collapse",type:Boolean,reflect:!0})],d.prototype,"noCollapse",void 0),(0,o.__decorate)([(0,a.Cb)()],d.prototype,"header",void 0),(0,o.__decorate)([(0,a.Cb)()],d.prototype,"secondary",void 0),(0,o.__decorate)([(0,a.SB)()],d.prototype,"_showContent",void 0),(0,o.__decorate)([(0,a.IO)(".container")],d.prototype,"_container",void 0),d=(0,o.__decorate)([(0,a.Mo)("ha-expansion-panel")],d)},80712:function(e,t,i){i.r(t),i.d(t,{HaIconButtonToggle:()=>s});var o=i(73742),r=i(59048),a=i(7616),n=i(78645);class s extends n.HaIconButton{constructor(...e){super(...e),this.selected=!1}}s.styles=r.iv`
    :host {
      position: relative;
    }
    mwc-icon-button {
      position: relative;
      transition: color 180ms ease-in-out;
    }
    mwc-icon-button::before {
      opacity: 0;
      transition: opacity 180ms ease-in-out;
      background-color: var(--primary-text-color);
      border-radius: 20px;
      height: 40px;
      width: 40px;
      content: "";
      position: absolute;
      top: -10px;
      left: -10px;
      bottom: -10px;
      right: -10px;
      margin: auto;
      box-sizing: border-box;
    }
    :host([border-only]) mwc-icon-button::before {
      background-color: transparent;
      border: 2px solid var(--primary-text-color);
    }
    :host([selected]) mwc-icon-button {
      color: var(--primary-background-color);
    }
    :host([selected]:not([disabled])) mwc-icon-button::before {
      opacity: 1;
    }
  `,(0,o.__decorate)([(0,a.Cb)({type:Boolean,reflect:!0})],s.prototype,"selected",void 0),s=(0,o.__decorate)([(0,a.Mo)("ha-icon-button-toggle")],s)},25661:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(73742),r=i(78722),a=i(59048),n=i(7616),s=i(60495),l=i(31132),d=e([s]);s=(d.then?(await d)():d)[0];class c extends a.fl{disconnectedCallback(){super.disconnectedCallback(),this._clearInterval()}connectedCallback(){super.connectedCallback(),this.datetime&&this._startInterval()}createRenderRoot(){return this}firstUpdated(e){super.firstUpdated(e),this._updateRelative()}update(e){super.update(e),this._updateRelative()}_clearInterval(){this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}_startInterval(){this._clearInterval(),this._interval=window.setInterval((()=>this._updateRelative()),6e4)}_updateRelative(){if(this.datetime){const e="string"==typeof this.datetime?(0,r.D)(this.datetime):this.datetime,t=(0,s.G)(e,this.hass.locale);this.innerHTML=this.capitalize?(0,l.f)(t):t}else this.innerHTML=this.hass.localize("ui.components.relative_time.never")}constructor(...e){super(...e),this.capitalize=!1}}(0,o.__decorate)([(0,n.Cb)({attribute:!1})],c.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],c.prototype,"datetime",void 0),(0,o.__decorate)([(0,n.Cb)({type:Boolean})],c.prototype,"capitalize",void 0),c=(0,o.__decorate)([(0,n.Mo)("ha-relative-time")],c),t()}catch(c){t(c)}}))},4820:function(e,t,i){var o=i(73742),r=i(1516),a=i(82028),n=i(59048),s=i(7616),l=i(19408);class d extends r.H{firstUpdated(){super.firstUpdated(),this.addEventListener("change",(()=>{this.haptic&&(0,l.j)("light")}))}constructor(...e){super(...e),this.haptic=!1}}d.styles=[a.W,n.iv`
      :host {
        --mdc-theme-secondary: var(--switch-checked-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__thumb {
        background-color: var(--switch-checked-button-color);
        border-color: var(--switch-checked-button-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__track {
        background-color: var(--switch-checked-track-color);
        border-color: var(--switch-checked-track-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb {
        background-color: var(--switch-unchecked-button-color);
        border-color: var(--switch-unchecked-button-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__track {
        background-color: var(--switch-unchecked-track-color);
        border-color: var(--switch-unchecked-track-color);
      }
    `],(0,o.__decorate)([(0,s.Cb)({type:Boolean})],d.prototype,"haptic",void 0),d=(0,o.__decorate)([(0,s.Mo)("ha-switch")],d)},19408:function(e,t,i){i.d(t,{j:()=>r});var o=i(29740);const r=e=>{(0,o.B)(window,"haptic",e)}},71785:function(e,t,i){var o=i(73742),r=i(59048),a=i(7616),n=(i(78645),i(52383));class s extends n.e{render(){return r.dy`
      <div class="container">
        <div class="content-wrapper">
          <slot name="primary"></slot>
          <slot name="secondary"></slot>
        </div>
        <!-- Filter Button - conditionally rendered based on filterValue -->
        ${this.filterValue?r.dy`
              <div class="filter-button ${this.filterActive?"filter-active":""}">
                <ha-icon-button
                  .path=${this.filterActive?"M21 8H3V6H21V8M13.81 16H10V18H13.09C13.21 17.28 13.46 16.61 13.81 16M18 11H6V13H18V11M21.12 15.46L19 17.59L16.88 15.46L15.47 16.88L17.59 19L15.47 21.12L16.88 22.54L19 20.41L21.12 22.54L22.54 21.12L20.41 19L22.54 16.88L21.12 15.46Z":"M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z"}
                  @click=${this._handleFilterClick}
                  .title=${this.knx.localize(this.filterActive?"knx_table_cell_filterable_filter_remove_tooltip":"knx_table_cell_filterable_filter_set_tooltip",{value:this.filterDisplayText||this.filterValue})}
                >
                </ha-icon-button>
              </div>
            `:r.Ld}
      </div>
    `}_handleFilterClick(e){e.stopPropagation(),this.dispatchEvent(new CustomEvent("toggle-filter",{bubbles:!0,composed:!0,detail:{value:this.filterValue,active:!this.filterActive}})),this.filterActive=!this.filterActive}constructor(...e){super(...e),this.filterActive=!1}}s.styles=[...n.e.styles,r.iv`
      .filter-button {
        display: none;
        flex-shrink: 0;
      }
      .container:hover .filter-button {
        display: block;
      }
      .filter-active {
        display: block;
        color: var(--primary-color);
      }
    `],(0,o.__decorate)([(0,a.Cb)({type:Object})],s.prototype,"knx",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],s.prototype,"filterValue",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],s.prototype,"filterDisplayText",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],s.prototype,"filterActive",void 0),s=(0,o.__decorate)([(0,a.Mo)("knx-table-cell-filterable")],s)},52383:function(e,t,i){i.d(t,{e:()=>n});var o=i(73742),r=i(59048),a=i(7616);class n extends r.oi{render(){return r.dy`
      <div class="container">
        <div class="content-wrapper">
          <slot name="primary"></slot>
          <slot name="secondary"></slot>
        </div>
      </div>
    `}}n.styles=[r.iv`
      :host {
        display: var(--knx-table-cell-display, block);
      }
      .container {
        padding: 4px 0;
        display: flex;
        align-items: center;
        flex-direction: row;
      }
      .content-wrapper {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }
      ::slotted(*) {
        overflow: hidden;
        text-overflow: ellipsis;
      }
      ::slotted(.primary) {
        font-weight: 500;
        margin-bottom: 2px;
      }
      ::slotted(.secondary) {
        color: var(--secondary-text-color);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    `],n=(0,o.__decorate)([(0,a.Mo)("knx-table-cell")],n)},59946:function(e,t,i){var o=i(73742),r=i(59048),a=i(7616),n=i(31733),s=i(86253),l=i(88245),d=(i(86776),i(86932)),c=(i(78645),i(80712),i(40830),i(73052),i(77204)),h=i(29740);const p="asc",u=new Intl.Collator(void 0,{numeric:!0,sensitivity:"base"});class g extends d.G{}g.styles=r.iv`
    /* Inherit base styles */
    ${d.G.styles}

    /* Add specific styles for flex content */
    :host {
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
    }

    .container.expanded {
      /* Keep original height: auto from base */
      /* Add requested styles */
      overflow: hidden !important;
      display: flex;
      flex-direction: column;
      flex: 1;
    }
  `,g=(0,o.__decorate)([(0,a.Mo)("flex-content-expansion-panel")],g);i(4820),i(79469),i(31914);class m extends r.oi{get _ascendingText(){return this.ascendingText??this.knx?.localize("knx_sort_menu_item_ascending")??""}get _descendingText(){return this.descendingText??this.knx?.localize("knx_sort_menu_item_descending")??""}render(){return r.dy`
      <mwc-list-item
        class="sort-row ${this.active?"active":""}"
        @click=${this._handleItemClick}
      >
        <div class="container">
          <div class="sort-field-name" title=${this.displayName} aria-label=${this.displayName}>
            ${this.displayName}
          </div>
          <div class="sort-buttons">
            <ha-icon-button
              class=${this.active&&this.direction===_.DESC?"active":""}
              .path=${this.descendingIcon}
              .label=${this._descendingText}
              .title=${this._descendingText}
              @click=${this._handleDescendingClick}
            ></ha-icon-button>
            <ha-icon-button
              class=${this.active&&this.direction===_.ASC?"active":""}
              .path=${this.ascendingIcon}
              .label=${this._ascendingText}
              .title=${this._ascendingText}
              @click=${this._handleAscendingClick}
            ></ha-icon-button>
          </div>
        </div>
      </mwc-list-item>
    `}_handleDescendingClick(e){e.stopPropagation(),(0,h.B)(this,"sort-option-selected",{criterion:this.criterion,direction:_.DESC})}_handleAscendingClick(e){e.stopPropagation(),(0,h.B)(this,"sort-option-selected",{criterion:this.criterion,direction:_.ASC})}_handleItemClick(){const e=this.active?this.direction===_.ASC?_.DESC:_.ASC:this.defaultDirection;(0,h.B)(this,"sort-option-selected",{criterion:this.criterion,direction:e})}constructor(...e){super(...e),this.criterion="idField",this.displayName="",this.defaultDirection=_.DEFAULT_DIRECTION,this.direction=_.ASC,this.active=!1,this.ascendingIcon=m.DEFAULT_ASC_ICON,this.descendingIcon=m.DEFAULT_DESC_ICON}}m.DEFAULT_ASC_ICON="M13,20H11V8L5.5,13.5L4.08,12.08L12,4.16L19.92,12.08L18.5,13.5L13,8V20Z",m.DEFAULT_DESC_ICON="M11,4H13V16L18.5,10.5L19.92,11.92L12,19.84L4.08,11.92L5.5,10.5L11,16V4Z",m.styles=r.iv`
    :host {
      display: block;
    }

    .sort-row {
      display: block;
      padding: 0 16px;
    }

    .sort-row.active {
      --mdc-theme-text-primary-on-background: var(--primary-color);
      background-color: var(--mdc-theme-surface-variant, rgba(var(--rgb-primary-color), 0.06));
      font-weight: 500;
    }

    .container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      height: 48px;
      gap: 10px;
    }

    .sort-field-name {
      display: flex;
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 1rem;
      align-items: center;
    }

    .sort-buttons {
      display: flex;
      align-items: center;
      min-width: 96px;
      justify-content: flex-end;
    }

    /* Hide sort buttons by default unless active */
    .sort-buttons ha-icon-button:not(.active) {
      display: none;
      color: var(--secondary-text-color);
    }

    /* Show sort buttons on row hover */
    .sort-row:hover .sort-buttons ha-icon-button {
      display: flex;
    }

    .sort-buttons ha-icon-button.active {
      display: flex;
      color: var(--primary-color);
    }
  `,(0,o.__decorate)([(0,a.Cb)({type:Object})],m.prototype,"knx",void 0),(0,o.__decorate)([(0,a.Cb)({type:String})],m.prototype,"criterion",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"display-name"})],m.prototype,"displayName",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"default-direction"})],m.prototype,"defaultDirection",void 0),(0,o.__decorate)([(0,a.Cb)({type:String})],m.prototype,"direction",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],m.prototype,"active",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"ascending-text"})],m.prototype,"ascendingText",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"descending-text"})],m.prototype,"descendingText",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"ascending-icon"})],m.prototype,"ascendingIcon",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"descending-icon"})],m.prototype,"descendingIcon",void 0),m=(0,o.__decorate)([(0,a.Mo)("knx-sort-menu-item")],m);class _ extends r.oi{updated(e){super.updated(e),(e.has("sortCriterion")||e.has("sortDirection"))&&this._updateMenuItems()}_updateMenuItems(){this._sortMenuItems&&this._sortMenuItems.forEach((e=>{e.active=e.criterion===this.sortCriterion,e.direction=e.criterion===this.sortCriterion?this.sortDirection:e.defaultDirection,e.knx=this.knx}))}render(){return r.dy`
      <div class="menu-container">
        <mwc-menu
          .corner=${"BOTTOM_START"}
          .fixed=${!0}
          @opened=${this._handleMenuOpened}
          @closed=${this._handleMenuClosed}
        >
          <slot name="header">
            <div class="header">
              <div class="title">
                <!-- Slot for custom title -->
                <slot name="title">${this.knx?.localize("knx_sort_menu_sort_by")??""}</slot>
              </div>
              <div class="toolbar">
                <!-- Slot for adding custom buttons to the header -->
                <slot name="toolbar"></slot>
              </div>
            </div>
            <li divider></li>
          </slot>

          <!-- Menu items will be slotted here -->
          <slot @sort-option-selected=${this._handleSortOptionSelected}></slot>
        </mwc-menu>
      </div>
    `}openMenu(e){this._menu&&(this._menu.anchor=e,this._menu.show())}closeMenu(){this._menu&&this._menu.close()}_updateSorting(e,t){e===this.sortCriterion&&t===this.sortDirection||(this.sortCriterion=e,this.sortDirection=t,(0,h.B)(this,"sort-changed",{criterion:e,direction:t}))}_handleMenuOpened(){this._updateMenuItems()}_handleMenuClosed(){}_handleSortOptionSelected(e){const{criterion:t,direction:i}=e.detail;this._updateSorting(t,i),this.closeMenu()}constructor(...e){super(...e),this.sortCriterion="",this.sortDirection=_.DEFAULT_DIRECTION}}_.ASC="asc",_.DESC="desc",_.DEFAULT_DIRECTION=_.ASC,_.styles=r.iv`
    .menu-container {
      position: relative;
      z-index: 1000;
      --mdc-list-vertical-padding: 0;
    }

    .header {
      position: sticky;
      top: 0;
      z-index: 1;
      background-color: var(--card-background-color, #fff);
      border-bottom: 1px solid var(--divider-color);
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      height: 48px;
      gap: 20px;
      width: 100%;
      box-sizing: border-box;
    }

    .header .title {
      font-size: 14px;
      color: var(--secondary-text-color);
      font-weight: 500;
      flex: 1;
    }

    .header .toolbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0px;
    }

    .menu-header .title {
      font-size: 14px;
      color: var(--secondary-text-color);
    }
  `,(0,o.__decorate)([(0,a.Cb)({type:Object})],_.prototype,"knx",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"sort-criterion"})],_.prototype,"sortCriterion",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"sort-direction"})],_.prototype,"sortDirection",void 0),(0,o.__decorate)([(0,a.IO)("mwc-menu")],_.prototype,"_menu",void 0),(0,o.__decorate)([(0,a.NH)({selector:"knx-sort-menu-item"})],_.prototype,"_sortMenuItems",void 0),_=(0,o.__decorate)([(0,a.Mo)("knx-sort-menu")],_);class x extends r.oi{setHeight(e,t=!0){const i=Math.max(this.minHeight,Math.min(this.maxHeight,e));t?(this._isTransitioning=!0,this.height=i,setTimeout((()=>{this._isTransitioning=!1}),this.animationDuration)):this.height=i}expand(){this.setHeight(this.maxHeight)}collapse(){this.setHeight(this.minHeight)}toggle(){const e=this.minHeight+.5*(this.maxHeight-this.minHeight);this.height<=e?this.expand():this.collapse()}get expansionRatio(){return(this.height-this.minHeight)/(this.maxHeight-this.minHeight)}render(){return r.dy`
      <div
        class="separator-container ${this.customClass}"
        style="
          height: ${this.height}px;
          transition: ${this._isTransitioning?`height ${this.animationDuration}ms ease-in-out`:"none"};
        "
      >
        <div class="content">
          <slot></slot>
        </div>
      </div>
    `}constructor(...e){super(...e),this.height=1,this.maxHeight=50,this.minHeight=1,this.animationDuration=150,this.customClass="",this._isTransitioning=!1}}x.styles=r.iv`
    :host {
      display: block;
      width: 100%;
      position: relative;
    }

    .separator-container {
      width: 100%;
      overflow: hidden;
      position: relative;
      display: flex;
      flex-direction: column;
      background: var(--card-background-color, var(--primary-background-color));
    }

    .content {
      flex: 1;
      overflow: hidden;
      position: relative;
    }

    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
      .separator-container {
        transition: none !important;
      }
    }
  `,(0,o.__decorate)([(0,a.Cb)({type:Number,reflect:!0})],x.prototype,"height",void 0),(0,o.__decorate)([(0,a.Cb)({type:Number,attribute:"max-height"})],x.prototype,"maxHeight",void 0),(0,o.__decorate)([(0,a.Cb)({type:Number,attribute:"min-height"})],x.prototype,"minHeight",void 0),(0,o.__decorate)([(0,a.Cb)({type:Number,attribute:"animation-duration"})],x.prototype,"animationDuration",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"custom-class"})],x.prototype,"customClass",void 0),(0,o.__decorate)([(0,a.SB)()],x.prototype,"_isTransitioning",void 0),x=(0,o.__decorate)([(0,a.Mo)("knx-separator")],x);class f extends r.oi{_computeFilterSortedOptions(){const e=this._computeFilteredOptions(),t=this._getComparator();return this._sortOptions(e,t,this.sortDirection)}_computeFilterSortedOptionsWithSeparator(){const e=this._computeFilteredOptions(),t=this._getComparator(),i=[],o=[];for(const r of e)r.selected?i.push(r):o.push(r);return{selected:this._sortOptions(i,t,this.sortDirection),unselected:this._sortOptions(o,t,this.sortDirection)}}_computeFilteredOptions(){const{data:e,config:{idField:t,primaryField:i,secondaryField:o,badgeField:r},selectedOptions:a=[]}=this,n=e.map((e=>{const n=t.mapper(e),s=i.mapper(e);if(!n||!s)throw new Error("Missing id or primary field on item: "+JSON.stringify(e));return{idField:n,primaryField:s,secondaryField:o.mapper(e),badgeField:r.mapper(e),selected:a.includes(n)}}));return this._applyFilterToOptions(n)}_getComparator(){const{config:e,defaultComparators:t,sortCriterion:i}=this;return e[i]?.comparator??t[i]}firstUpdated(){this._setupSeparatorScrollHandler()}updated(e){(e.has("expanded")||e.has("pinSelectedItems"))&&requestAnimationFrame((()=>{this._setupSeparatorScrollHandler(),(e.has("expanded")&&this.expanded||e.has("pinSelectedItems")&&this.pinSelectedItems)&&requestAnimationFrame((()=>{this._handleSeparatorScroll()}))}))}disconnectedCallback(){super.disconnectedCallback(),this._cleanupSeparatorScrollHandler()}_setupSeparatorScrollHandler(){this._cleanupSeparatorScrollHandler(),this._boundScrollHandler||(this._boundScrollHandler=this._handleSeparatorScroll.bind(this)),this.pinSelectedItems&&this._optionsListContainer&&this._optionsListContainer.addEventListener("scroll",this._boundScrollHandler,{passive:!0})}_cleanupSeparatorScrollHandler(){this._boundScrollHandler&&this._optionsListContainer&&this._optionsListContainer.removeEventListener("scroll",this._boundScrollHandler)}_handleSeparatorScroll(){if(!(this.pinSelectedItems&&this._separator&&this._optionsListContainer&&this._separatorContainer))return;const e=this._optionsListContainer.getBoundingClientRect(),t=this._separatorContainer.getBoundingClientRect().top-e.top,i=this._separatorScrollZone;if(t<=i&&t>=0){const e=1-t/i,o=this._separatorMinHeight+e*(this._separatorMaxHeight-this._separatorMinHeight);this._separator.setHeight(Math.round(o),!1)}else if(t>i){(this._separator.height||this._separatorMinHeight)!==this._separatorMinHeight&&this._separator.setHeight(this._separatorMinHeight,!1)}}_handleSeparatorClick(){this._optionsListContainer&&this._optionsListContainer.scrollTo({top:0,behavior:"smooth"})}_applyFilterToOptions(e){if(!this.filterQuery)return e;const t=this.filterQuery.toLowerCase(),{idField:i,primaryField:o,secondaryField:r,badgeField:a}=this.config,n=[];return i.filterable&&n.push((e=>e.idField)),o.filterable&&n.push((e=>e.primaryField)),r.filterable&&n.push((e=>e.secondaryField)),a.filterable&&n.push((e=>e.badgeField)),e.filter((e=>n.some((i=>{const o=i(e);return"string"==typeof o&&o.toLowerCase().includes(t)}))))}_sortOptions(e,t,i=p){const o=i===p?1:-1;return[...e].sort(((e,i)=>t(e,i)*o))}_handleSearchChange(e){this.filterQuery=e.detail.value}_handleSortButtonClick(e){e.stopPropagation();const t=this.shadowRoot?.querySelector("knx-sort-menu");t&&t.openMenu(e.currentTarget)}_handleSortChanged(e){this.sortCriterion=e.detail.criterion,this.sortDirection=e.detail.direction}_handlePinButtonClick(e){e.stopPropagation(),this.pinSelectedItems=!this.pinSelectedItems}_handleClearFiltersButtonClick(e){e.stopPropagation(),e.preventDefault(),this._setSelectedOptions([])}_setSelectedOptions(e){this.selectedOptions=e,(0,h.B)(this,"selection-changed",{value:this.selectedOptions})}_getSortIcon(){return this.sortDirection===p?"M19 17H22L18 21L14 17H17V3H19M2 17H12V19H2M6 5V7H2V5M2 11H9V13H2V11Z":"M19 7H22L18 3L14 7H17V21H19M2 17H12V19H2M6 5V7H2V5M2 11H9V13H2V11Z"}_hasFilterableOrSortableFields(){return!!this.config&&Object.values(this.config).some((e=>e.filterable||e.sortable))}_hasFilterableFields(){return!!this.config&&Object.values(this.config).some((e=>e.filterable))}_hasSortableFields(){return!!this.config&&Object.values(this.config).some((e=>e.sortable))}_expandedChanged(e){this.expanded=e.detail.expanded,(0,h.B)(this,"expanded-changed",{expanded:this.expanded})}_handleOptionItemClick(e){const t=e.currentTarget.getAttribute("data-value");t&&this._toggleOption(t)}_toggleOption(e){this.selectedOptions?.includes(e)?this._setSelectedOptions(this.selectedOptions?.filter((t=>t!==e))??[]):this._setSelectedOptions([...this.selectedOptions??[],e]),requestAnimationFrame((()=>{this._handleSeparatorScroll()}))}_renderFilterControl(){return r.dy`
      <div class="filter-toolbar">
        <div class="search">
          ${this._hasFilterableFields()?r.dy`
                <search-input-outlined
                  .hass=${this.hass}
                  .filter=${this.filterQuery}
                  @value-changed=${this._handleSearchChange}
                ></search-input-outlined>
              `:r.Ld}
        </div>
        ${this._hasSortableFields()?r.dy`
              <div class="buttons">
                <ha-icon-button
                  class="sort-button"
                  .path=${this._getSortIcon()}
                  title=${this.sortDirection===p?this.knx.localize("knx_list_filter_sort_ascending_tooltip"):this.knx.localize("knx_list_filter_sort_descending_tooltip")}
                  @click=${this._handleSortButtonClick}
                ></ha-icon-button>

                <knx-sort-menu
                  .sortCriterion=${this.sortCriterion}
                  .sortDirection=${this.sortDirection}
                  @sort-changed=${this._handleSortChanged}
                >
                  <div slot="title">${this.knx.localize("knx_list_filter_sort_by")}</div>

                  <!-- Toolbar with additional controls like pin button -->
                  <div slot="toolbar">
                    <!-- Pin Button for keeping selected items at top -->
                    <ha-icon-button-toggle
                      .path=${"M16,12V4H17V2H7V4H8V12L6,14V16H11.2V22H12.8V16H18V14L16,12Z"}
                      .selected=${this.pinSelectedItems}
                      @click=${this._handlePinButtonClick}
                      title=${this.knx.localize("knx_list_filter_selected_items_on_top")}
                    >
                    </ha-icon-button-toggle>
                  </div>
                  <!-- Sort menu items generated from sortable fields -->
                  ${Object.entries(this.config||{}).map((([e,t])=>t.sortable?r.dy`
                          <knx-sort-menu-item
                            criterion=${e}
                            display-name=${t.fieldName}
                            default-direction=${t.sortDefaultDirection??"asc"}
                            ascending-text=${t.sortAscendingText??this.knx.localize("knx_list_filter_sort_ascending")}
                            descending-text=${t.sortDescendingText??this.knx.localize("knx_list_filter_sort_descending")}
                          ></knx-sort-menu-item>
                        `:r.Ld))}
                </knx-sort-menu>
              </div>
            `:r.Ld}
      </div>
    `}_renderOptionsList(){return r.dy`
      ${(0,s.l)([this.filterQuery,this.sortDirection,this.sortCriterion,this.data,this.selectedOptions,this.expanded,this.config,this.pinSelectedItems],(()=>this.pinSelectedItems?this._renderPinnedOptionsList():this._renderRegularOptionsList()))}
    `}_renderPinnedOptionsList(){const e=this.knx.localize("knx_list_filter_no_results"),{selected:t,unselected:i}=this._computeFilterSortedOptionsWithSeparator();return 0===t.length&&0===i.length?r.dy`<div class="empty-message" role="alert">${e}</div>`:r.dy`
      <div class="options-list" tabindex="0">
        <!-- Render selected items first -->
        ${t.length>0?r.dy`
              ${(0,l.r)(t,(e=>e.idField),(e=>this._renderOptionItem(e)))}
            `:r.Ld}

        <!-- Render separator between selected and unselected items -->
        ${t.length>0&&i.length>0?r.dy`
              <div class="separator-container">
                <knx-separator
                  .height=${this._separator?.height||this._separatorMinHeight}
                  .maxHeight=${this._separatorMaxHeight}
                  .minHeight=${this._separatorMinHeight}
                  .animationDuration=${this._separatorAnimationDuration}
                  customClass="list-separator"
                >
                  <div class="separator-content" @click=${this._handleSeparatorClick}>
                    <ha-svg-icon .path=${"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"}></ha-svg-icon>
                    <span class="separator-text">
                      ${this.knx.localize("knx_list_filter_scroll_to_selection")}
                    </span>
                  </div>
                </knx-separator>
              </div>
            `:r.Ld}

        <!-- Render unselected items -->
        ${i.length>0?r.dy`
              ${(0,l.r)(i,(e=>e.idField),(e=>this._renderOptionItem(e)))}
            `:r.Ld}
      </div>
    `}_renderRegularOptionsList(){const e=this.knx.localize("knx_list_filter_no_results"),t=this._computeFilterSortedOptions();return 0===t.length?r.dy`<div class="empty-message" role="alert">${e}</div>`:r.dy`
      <div class="options-list" tabindex="0">
        ${(0,l.r)(t,(e=>e.idField),(e=>this._renderOptionItem(e)))}
      </div>
    `}_renderOptionItem(e){const t={"option-item":!0,selected:e.selected};return r.dy`
      <div
        class=${(0,n.$)(t)}
        role="option"
        aria-selected=${e.selected}
        @click=${this._handleOptionItemClick}
        data-value=${e.idField}
      >
        <div class="option-content">
          <div class="option-primary">
            <span class="option-label" title=${e.primaryField}>${e.primaryField}</span>
            ${e.badgeField?r.dy`<span class="option-badge">${e.badgeField}</span>`:r.Ld}
          </div>

          ${e.secondaryField?r.dy`
                <div class="option-secondary" title=${e.secondaryField}>
                  ${e.secondaryField}
                </div>
              `:r.Ld}
        </div>

        <ha-checkbox
          .checked=${e.selected}
          .value=${e.idField}
          tabindex="-1"
          pointer-events="none"
        ></ha-checkbox>
      </div>
    `}render(){const e=this.selectedOptions?.length??0,t=this.filterTitle||this.knx.localize("knx_list_filter_title"),i=this.knx.localize("knx_list_filter_clear");return r.dy`
      <flex-content-expansion-panel
        leftChevron
        .expanded=${this.expanded}
        @expanded-changed=${this._expandedChanged}
      >
        <!-- Header with title and clear selection control -->
        <div slot="header" class="header">
          <span class="title">
            ${t}
            ${e?r.dy`<div class="badge">${e}</div>`:r.Ld}
          </span>
          <div class="controls">
            ${e?r.dy`
                  <ha-icon-button
                    .path=${"M21 8H3V6H21V8M13.81 16H10V18H13.09C13.21 17.28 13.46 16.61 13.81 16M18 11H6V13H18V11M21.12 15.46L19 17.59L16.88 15.46L15.47 16.88L17.59 19L15.47 21.12L16.88 22.54L19 20.41L21.12 22.54L22.54 21.12L20.41 19L22.54 16.88L21.12 15.46Z"}
                    @click=${this._handleClearFiltersButtonClick}
                    .title=${i}
                  ></ha-icon-button>
                `:r.Ld}
          </div>
        </div>

        <!-- Render filter content only when panel is expanded and visible -->
        ${this.expanded?r.dy`
              <div class="filter-content">
                ${this._hasFilterableOrSortableFields()?this._renderFilterControl():r.Ld}
              </div>

              <!-- Filter options list - moved outside filter-content for proper sticky behavior -->
              <div class="options-list-wrapper ha-scrollbar">${this._renderOptionsList()}</div>
            `:r.Ld}
      </flex-content-expansion-panel>
    `}static get styles(){return[c.$c,r.iv`
        :host {
          display: flex;
          flex-direction: column;
          border-bottom: 1px solid var(--divider-color);
        }
        :host([expanded]) {
          flex: 1;
          height: 0;
          overflow: hidden;
        }

        flex-content-expansion-panel {
          --ha-card-border-radius: 0;
          --expansion-panel-content-padding: 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          width: 100%;
        }

        .title {
          display: flex;
          align-items: center;
          font-weight: 500;
        }

        .badge {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          margin-left: 8px;
          min-width: 20px;
          height: 20px;
          box-sizing: border-box;
          border-radius: 50%;
          font-weight: 500;
          font-size: 12px;
          background-color: var(--primary-color);
          line-height: 1;
          text-align: center;
          padding: 0 4px;
          color: var(--text-primary-color);
        }

        .controls {
          display: flex;
          align-items: center;
          margin-left: auto;
        }

        .header ha-icon-button {
          margin-inline-end: 4px;
        }

        .filter-content {
          display: flex;
          flex-direction: column;
          flex-shrink: 0;
        }

        .options-list-wrapper {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        .options-list {
          display: block;
          padding: 0;
          flex: 1;
        }

        .filter-toolbar {
          display: flex;
          align-items: center;
          padding: 0px 8px;
          gap: 4px;
          border-bottom: 1px solid var(--divider-color);
        }

        .search {
          flex: 1;
        }

        .buttons:last-of-type {
          margin-right: -8px;
        }

        search-input-outlined {
          display: block;
          flex: 1;
          padding: 8px 0;
        }

        .option-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding-left: 16px;
          min-height: 48px;
          cursor: pointer;
          position: relative;
        }
        .option-item:hover {
          background-color: rgba(var(--rgb-primary-text-color), 0.04);
        }
        .option-item.selected {
          background-color: var(--mdc-theme-surface-variant, rgba(var(--rgb-primary-color), 0.06));
        }

        .option-content {
          display: flex;
          flex-direction: column;
          width: 100%;
          min-width: 0;
          height: 100%;
        }

        .option-primary {
          display: flex;
          justify-content: space-between;
          align-items: center;
          width: 100%;
          margin-bottom: 4px;
        }

        .option-label {
          font-weight: 500;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .option-secondary {
          color: var(--secondary-text-color);
          font-size: 0.85em;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .option-badge {
          display: inline-flex;
          background-color: rgba(var(--rgb-primary-color), 0.15);
          color: var(--primary-color);
          font-weight: 500;
          font-size: 0.75em;
          padding: 1px 6px;
          border-radius: 10px;
          min-width: 20px;
          height: 16px;
          align-items: center;
          justify-content: center;
          margin-left: 8px;
          vertical-align: middle;
        }

        .empty-message {
          text-align: center;
          padding: 16px;
          color: var(--secondary-text-color);
        }

        /* Prevent checkbox from capturing clicks */
        ha-checkbox {
          pointer-events: none;
        }

        knx-sort-menu ha-icon-button-toggle {
          --mdc-icon-button-size: 36px; /* Default is 48px */
          --mdc-icon-size: 18px; /* Default is 24px */
          color: var(--secondary-text-color);
        }

        knx-sort-menu ha-icon-button-toggle[selected] {
          --primary-background-color: var(--primary-color);
          --primary-text-color: transparent;
        }

        /* Separator Styling */
        .separator-container {
          position: sticky;
          top: 0;
          z-index: 10;
          background: var(--card-background-color);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .separator-content {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 6px;
          padding: 8px;
          background: var(--primary-color);
          color: var(--text-primary-color);
          font-size: 0.8em;
          font-weight: 500;
          cursor: pointer;
          transition: opacity 0.2s ease;
          user-select: none;
          box-sizing: border-box;
        }

        .separator-content:hover {
          opacity: 0.9;
        }

        .separator-content ha-svg-icon {
          --mdc-icon-size: 16px;
        }

        .separator-text {
          text-align: center;
        }

        .list-separator {
          position: relative;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Enhanced separator visibility when scrolled */
        .options-list:not(:hover) .separator-container {
          transition: box-shadow 0.2s ease;
        }
      `]}constructor(...e){super(...e),this.data=[],this.expanded=!1,this.narrow=!1,this.pinSelectedItems=!0,this.filterQuery="",this.sortCriterion="primaryField",this.sortDirection="asc",this._separatorMaxHeight=28,this._separatorMinHeight=2,this._separatorAnimationDuration=150,this._separatorScrollZone=28,this.defaultComparators={idField:(e,t)=>u.compare(e.idField,t.idField),primaryField:(e,t)=>u.compare(e.primaryField??"",t.primaryField??"")||u.compare(e.secondaryField??"",t.secondaryField??"")||u.compare(e.badgeField??"",t.badgeField??"")||u.compare(e.idField,t.idField),secondaryField:(e,t)=>u.compare(e.secondaryField??"",t.secondaryField??"")||u.compare(e.primaryField??"",t.primaryField??"")||u.compare(e.badgeField??"",t.badgeField??"")||u.compare(e.idField,t.idField),badgeField:(e,t)=>u.compare(e.badgeField??"",t.badgeField??"")||u.compare(e.primaryField??"",t.primaryField??"")||u.compare(e.secondaryField??"",t.secondaryField??"")||u.compare(e.idField,t.idField)}}}(0,o.__decorate)([(0,a.Cb)({attribute:!1,hasChanged:()=>!1})],f.prototype,"hass",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],f.prototype,"knx",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],f.prototype,"data",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],f.prototype,"selectedOptions",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],f.prototype,"config",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean,reflect:!0})],f.prototype,"expanded",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean})],f.prototype,"narrow",void 0),(0,o.__decorate)([(0,a.Cb)({type:Boolean,attribute:"pin-selected-items"})],f.prototype,"pinSelectedItems",void 0),(0,o.__decorate)([(0,a.Cb)({type:String,attribute:"filter-title"})],f.prototype,"filterTitle",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"filter-query"})],f.prototype,"filterQuery",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"sort-criterion"})],f.prototype,"sortCriterion",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:"sort-direction"})],f.prototype,"sortDirection",void 0),(0,o.__decorate)([(0,a.IO)("knx-separator")],f.prototype,"_separator",void 0),(0,o.__decorate)([(0,a.IO)(".options-list-wrapper")],f.prototype,"_optionsListContainer",void 0),(0,o.__decorate)([(0,a.IO)(".separator-container")],f.prototype,"_separatorContainer",void 0),f=(0,o.__decorate)([(0,a.Mo)("knx-list-filter")],f)},84986:function(e,t,i){var o=i(73742),r=i(59048),a=i(7616);class n extends r.oi{render(){return r.dy`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            <div class="header-title">
              <slot name="title"></slot>
            </div>
            <div class="header-subtitle">
              <slot name="subtitle"></slot>
            </div>
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `}static get styles(){return[r.iv`
        :host {
          display: block;
        }
        :host([show-border]) {
          border-bottom: 1px solid var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }
        .header-bar {
          display: flex;
          flex-direction: row;
          align-items: center;
          padding: 4px 24px 4px 24px;
          box-sizing: border-box;
          gap: 12px;
        }
        .header-content {
          flex: 1;
          padding: 10px 4px;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header-title {
          font-size: 22px;
          line-height: 28px;
          font-weight: 400;
        }
        .header-subtitle {
          margin-top: 2px;
          font-size: 14px;
          color: var(--secondary-text-color);
        }

        .header-navigation-icon {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
        .header-action-items {
          flex: none;
          min-width: 8px;
          height: 100%;
          display: flex;
          flex-direction: row;
        }
      `]}constructor(...e){super(...e),this.showBorder=!1}}(0,o.__decorate)([(0,a.Cb)({type:Boolean,reflect:!0,attribute:"show-border"})],n.prototype,"showBorder",void 0),n=(0,o.__decorate)([(0,a.Mo)("knx-dialog-header")],n)},76606:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(73742),r=(i(98334),i(59048)),a=i(7616),n=i(29740),s=i(77204),l=(i(40830),i(84986),i(65793)),d=i(25661),c=(i(78645),i(99298),e([d]));d=(c.then?(await c)():c)[0];const h="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z",p="M4,11V13H16L10.5,18.5L11.92,19.92L19.84,12L11.92,4.08L10.5,5.5L16,11H4Z",u="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z";class g extends r.oi{connectedCallback(){super.connectedCallback(),this._handleKeyDown=this._handleKeyDown.bind(this),document.addEventListener("keydown",this._handleKeyDown)}disconnectedCallback(){document.removeEventListener("keydown",this._handleKeyDown),super.disconnectedCallback()}closeDialog(){this.telegram=void 0,(0,n.B)(this,"dialog-closed",{dialog:this.localName},{bubbles:!1})}_checkScrolled(e){const t=e.target,i=this.shadowRoot?.querySelector("knx-dialog-header");i&&t.scrollTop>0?i.showBorder=!0:i&&(i.showBorder=!1)}render(){if(!this.telegram)return this.closeDialog(),r.Ld;const e="Outgoing"===this.telegram.direction?"outgoing":"incoming";return r.dy`
      <!-- 
        The .heading property is required for the header slot to be rendered,
        even though we override it with our custom knx-dialog-header component.
        The value is not displayed but must be truthy for the slot to work.
      -->
      <ha-dialog open @closed=${this.closeDialog} .heading=${" "}>
        <knx-dialog-header slot="heading" .showBorder=${!0}>
          <ha-icon-button
            slot="navigationIcon"
            .label=${this.hass.localize("ui.dialogs.generic.close")}
            .path=${u}
            dialogAction="close"
            class="close-button"
          ></ha-icon-button>
          <div slot="title" class="header-title">
            ${this.knx.localize("knx_telegram_info_dialog_telegram")}
          </div>
          <div slot="subtitle">
            <span title=${(0,l.Am)(this.telegram.timestampIso)}>
              ${(0,l.q$)(this.telegram.timestamp)+" "}
            </span>
            (<ha-relative-time
              .hass=${this.hass}
              .datetime=${this.telegram.timestamp}
              .capitalize=${!1}
            ></ha-relative-time
            >)
          </div>
          <div slot="actionItems" class="direction-badge ${e}">
            ${this.knx.localize(this.telegram.direction)}
          </div>
        </knx-dialog-header>
        <div class="content" @scroll=${this._checkScrolled}>
          <!-- Body: addresses + value + details -->
          <div class="telegram-body">
            <div class="addresses-row">
              <div class="address-item">
                <div class="item-label">
                  ${this.knx.localize("knx_telegram_info_dialog_source")}
                </div>
                <div class="address-chip">${this.telegram.sourceAddress}</div>
                ${this.telegram.sourceText?r.dy`<div class="item-name">${this.telegram.sourceText}</div>`:r.Ld}
              </div>
              <div class="address-item">
                <div class="item-label">
                  ${this.knx.localize("knx_telegram_info_dialog_destination")}
                </div>
                <div class="address-chip">${this.telegram.destinationAddress}</div>
                ${this.telegram.destinationText?r.dy`<div class="item-name">${this.telegram.destinationText}</div>`:r.Ld}
              </div>
            </div>

            ${null!=this.telegram.value?r.dy`
                  <div class="value-section">
                    <div class="value-label">
                      ${this.knx.localize("knx_telegram_info_dialog_value")}
                    </div>
                    <div class="value-content">${this.telegram.value}</div>
                  </div>
                `:r.Ld}

            <div class="telegram-details">
              <div class="detail-grid">
                <div class="detail-item">
                  <div class="detail-label">
                    ${this.knx.localize("knx_telegram_info_dialog_type")}
                  </div>
                  <div class="detail-value">${this.telegram.type}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">DPT</div>
                  <div class="detail-value">${this.telegram.dpt||""}</div>
                </div>
                ${null!=this.telegram.payload?r.dy`
                      <div class="detail-item payload">
                        <div class="detail-label">
                          ${this.knx.localize("knx_telegram_info_dialog_payload")}
                        </div>
                        <code>${this.telegram.payload}</code>
                      </div>
                    `:r.Ld}
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation buttons: previous / next -->
        <div slot="secondaryAction" style="margin: 0;">
          <mwc-button
            class="nav-button"
            @click=${this._previousTelegram}
            .disabled=${this.disablePrevious}
          >
            <ha-svg-icon .path=${h}></ha-svg-icon>
            ${this.hass.localize("ui.common.previous")}
          </mwc-button>
        </div>
        <div slot="primaryAction">
          <mwc-button class="nav-button" @click=${this._nextTelegram} .disabled=${this.disableNext}>
            ${this.hass.localize("ui.common.next")}
            <ha-svg-icon .path=${p}></ha-svg-icon>
          </mwc-button>
        </div>
      </ha-dialog>
    `}_nextTelegram(){(0,n.B)(this,"next-telegram",void 0,{bubbles:!0})}_previousTelegram(){(0,n.B)(this,"previous-telegram",void 0,{bubbles:!0})}_handleKeyDown(e){if(this.telegram)switch(e.key){case"ArrowLeft":case"ArrowDown":this.disablePrevious||(e.preventDefault(),this._previousTelegram());break;case"ArrowRight":case"ArrowUp":this.disableNext||(e.preventDefault(),this._nextTelegram())}}static get styles(){return[s.yu,r.iv`
        ha-dialog {
          --vertical-align-dialog: center;
          --dialog-z-index: 20;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          /* When in fullscreen dialog should be attached to top */
          ha-dialog {
            --dialog-surface-margin-top: 0px;
            --dialog-content-padding: 16px 24px 16px 24px;
          }
        }
        @media all and (min-width: 600px) and (min-height: 501px) {
          /* Set the dialog width and min-height, but let height adapt to content */
          ha-dialog {
            --mdc-dialog-min-width: 580px;
            --mdc-dialog-max-width: 580px;
            --mdc-dialog-min-height: 70%;
            --mdc-dialog-max-height: 100%;
            --dialog-content-padding: 16px 24px 16px 24px;
          }
        }

        /* Custom heading styles */
        .custom-heading {
          display: flex;
          flex-direction: row;
          padding: 16px 24px 12px 16px;
          border-bottom: 1px solid var(--divider-color);
          align-items: center;
          gap: 12px;
        }
        .heading-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }
        .header-title {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
          line-height: 1.3;
          color: var(--primary-text-color);
        }
        .close-button {
          color: var(--primary-text-color);
          margin-right: -8px;
        }

        /* General content styling */
        .content {
          display: flex;
          flex-direction: column;
          flex: 1;
          gap: 16px;
          outline: none;
        }

        /* Timestamp style */
        .timestamp {
          font-size: 13px;
          color: var(--secondary-text-color);
          margin-top: 2px;
        }
        .direction-badge {
          font-size: 12px;
          font-weight: 500;
          padding: 3px 10px;
          border-radius: 12px;
          text-transform: uppercase;
          letter-spacing: 0.4px;
          white-space: nowrap;
        }
        .direction-badge.outgoing {
          background-color: var(--knx-blue, var(--info-color));
          color: var(--text-primary-color, #fff);
        }
        .direction-badge.incoming {
          background-color: var(--knx-green, var(--success-color));
          color: var(--text-primary-color, #fff);
        }

        /* Body: addresses + value + details */
        .telegram-body {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .addresses-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }
        @media (max-width: 450px) {
          .addresses-row {
            grid-template-columns: 1fr;
            gap: 12px;
          }
        }
        .address-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
          background: var(--card-background-color);
          padding: 0px 12px 0px 12px;
          border-radius: 8px;
        }
        .item-label {
          font-size: 13px;
          font-weight: 500;
          color: var(--secondary-text-color);
          margin-bottom: 4px;
          letter-spacing: 0.5px;
        }
        .address-chip {
          font-family: var(--code-font-family, monospace);
          font-size: 16px;
          font-weight: 500;
          background: var(--secondary-background-color);
          border-radius: 12px;
          padding: 6px 12px;
          text-align: center;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .item-name {
          font-size: 12px;
          color: var(--secondary-text-color);
          font-style: italic;
          margin-top: 4px;
          text-align: center;
        }

        /* Value section */
        .value-section {
          padding: 16px;
          background: var(--primary-background-color);
          border-radius: 8px;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .value-label {
          font-size: 13px;
          color: var(--secondary-text-color);
          margin-bottom: 8px;
          font-weight: 500;
          letter-spacing: 0.4px;
        }
        .value-content {
          font-family: var(--code-font-family, monospace);
          font-size: 22px;
          font-weight: 600;
          color: var(--primary-color);
          text-align: center;
        }

        /* Telegram details (type/DPT/payload) */
        .telegram-details {
          padding: 16px;
          background: var(--secondary-background-color);
          border-radius: 8px;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.06);
        }
        .detail-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
        }
        .detail-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .detail-item.payload {
          grid-column: span 2;
          margin-top: 4px;
        }
        .detail-label {
          font-size: 13px;
          color: var(--secondary-text-color);
          font-weight: 500;
        }
        .detail-value {
          font-size: 14px;
          font-weight: 500;
        }
        code {
          font-family: var(--code-font-family, monospace);
          font-size: 13px;
          background: var(--card-background-color);
          padding: 8px 12px;
          border-radius: 6px;
          display: block;
          overflow-x: auto;
          white-space: pre;
          box-shadow: 0 1px 2px rgba(var(--rgb-primary-text-color), 0.04);
          margin-top: 4px;
        }

        /* Navigation buttons */
        .nav-button {
          --mdc-theme-primary: var(--primary-color);
          --mdc-button-disabled-ink-color: var(--disabled-text-color);
          display: flex;
          align-items: center;
          gap: 8px;
          min-width: 100px;
        }
        .nav-button ha-svg-icon {
          --mdc-icon-size: 18px;
        }
      `]}constructor(...e){super(...e),this.disableNext=!1,this.disablePrevious=!1}}(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"hass",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"knx",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"telegram",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"disableNext",void 0),(0,o.__decorate)([(0,a.Cb)({attribute:!1})],g.prototype,"disablePrevious",void 0),g=(0,o.__decorate)([(0,a.Mo)("knx-telegram-info-dialog")],g),t()}catch(h){t(h)}}))},14160:function(e,t,i){i.d(t,{g:()=>r});var o=i(65793);class r{constructor(e){this.offset=new Date(0);const t=/[^a-zA-Z0-9]/g,i=/[^0-9]/g,r=e=>e.replace(t,""),a=e=>e.replace(i,"");this.id=[r(e.timestamp),r(e.source),r(e.destination)].join("_"),this.timestampIso=e.timestamp,this.timestamp=new Date(e.timestamp),this.sourceAddress=e.source,this.sourceText=e.source_name,this.sourceAddressNumeric=parseInt(a(e.source),10),this.sourceName=`${e.source}: ${e.source_name}`,this.destinationAddress=e.destination,this.destinationText=e.destination_name,this.destinationAddressNumeric=parseInt(a(e.destination),10),this.destinationName=`${e.destination}: ${e.destination_name}`,this.type=e.telegramtype,this.direction=e.direction,this.payload=o.f3.payload(e),this.dpt=o.f3.dptNameNumber(e),this.unit=e.unit,this.value=o.f3.valueWithUnit(e)||this.payload||("GroupValueRead"===e.telegramtype?"GroupRead":"")}}},65793:function(e,t,i){i.d(t,{Am:()=>l,Wl:()=>a,Yh:()=>n,f3:()=>r,q$:()=>s,xi:()=>d});var o=i(24110);const r={payload:e=>null==e.payload?"":Array.isArray(e.payload)?e.payload.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),"0x"):e.payload.toString(),valueWithUnit:e=>null==e.value?"":"number"==typeof e.value||"boolean"==typeof e.value||"string"==typeof e.value?e.value.toString()+(e.unit?" "+e.unit:""):(0,o.$w)(e.value),timeWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString(["en-US"],{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dateWithMilliseconds:e=>new Date(e.timestamp).toLocaleTimeString([],{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),dptNumber:e=>null==e.dpt_main?"":null==e.dpt_sub?e.dpt_main.toString():e.dpt_main.toString()+"."+e.dpt_sub.toString().padStart(3,"0"),dptNameNumber:e=>{const t=r.dptNumber(e);return null==e.dpt_name?`DPT ${t}`:t?`DPT ${t} ${e.dpt_name}`:e.dpt_name}},a=e=>null==e?"":e.main+(e.sub?"."+e.sub.toString().padStart(3,"0"):""),n=e=>e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),s=e=>e.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+e.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit",fractionalSecondDigits:3}),l=e=>{const t=new Date(e),i=e.match(/\.(\d{6})/),o=i?i[1]:"000000";return t.toLocaleDateString(void 0,{year:"numeric",month:"2-digit",day:"2-digit"})+", "+t.toLocaleTimeString(void 0,{hour12:!1,hour:"2-digit",minute:"2-digit",second:"2-digit"})+"."+o},d=e=>`${e.getUTCMinutes().toString().padStart(2,"0")}:${e.getUTCSeconds().toString().padStart(2,"0")}.${e.getUTCMilliseconds().toString().padStart(3,"0")}`},49613:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{KNXGroupMonitor:()=>k});var r=i(73742),a=i(59048),n=i(28105),s=i(86829),l=(i(7061),i(22543),i(98334),i(78645),i(77204)),d=i(29173),c=i(51597),h=(i(52383),i(71785),i(76606)),p=(i(59946),i(7616)),u=i(65793),g=i(63279),m=i(38059),_=i(14160),x=e([s,h]);[s,h]=x.then?(await x)():x;const f="M15,16H19V18H15V16M15,8H22V10H15V8M15,12H21V14H15V12M3,18A2,2 0 0,0 5,20H11A2,2 0 0,0 13,18V8H3V18M14,5H11L10,4H6L5,5H2V7H14V5Z",b="M13,6V18L21.5,12M4,18L12.5,12L4,6V18Z",v="M14,19H18V5H14M6,19H10V5H6V19Z",y="M17.65,6.35C16.2,4.9 14.21,4 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20C15.73,20 18.84,17.45 19.73,14H17.65C16.83,16.33 14.61,18 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6C13.66,6 15.14,6.69 16.22,7.78L13,11H20V4L17.65,6.35Z",w=new m.r("group_monitor");class k extends a.oi{static get styles(){return[l.Qx,a.iv`
        :host {
          --table-row-alternative-background-color: var(--primary-background-color);
        }

        ha-icon-button.active {
          color: var(--primary-color);
        }

        .table-header {
          border-bottom: 1px solid var(--divider-color);
          padding-bottom: 12px;
        }

        :host {
          --ha-data-table-row-style: {
            font-size: 0.9em;
            padding: 8px 0;
          };
        }

        .filter-wrapper {
          display: flex;
          flex-direction: column;
        }

        .toolbar-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      `]}get filteredRows(){return this._getFilteredRows(this._telegrams,JSON.stringify(this._filters),this._sortColumn)}willUpdate(e){e.has("route")&&this.route&&this._setFiltersFromUrl()}async firstUpdated(){if(!this._subscribed&&await this._loadRecentTelegrams())try{this._subscribed=await(0,g.IP)(this.hass,(e=>this._handleIncomingTelegram(e))),this._connectionError=null}catch(e){w.error("Failed to subscribe to telegrams",e),this._connectionError=e instanceof Error?e.message:String(e)}}disconnectedCallback(){super.disconnectedCallback(),this._unsubscribe()}get searchLabel(){if(this.narrow)return this.knx.localize("group_monitor_search_label_narrow");const e=this.filteredRows.length,t=1===e?"group_monitor_search_label_singular":"group_monitor_search_label";return this.knx.localize(t,{count:e})}get sourceDistinctValuesArray(){return Object.values(this._distinctValues.source)}get destinationDistinctValuesArray(){return Object.values(this._distinctValues.destination)}get directionDistinctValuesArray(){return Object.values(this._distinctValues.direction)}get telegramTypeDistinctValuesArray(){return Object.values(this._distinctValues.telegramtype)}get _sourceFilterConfig(){return{idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_primaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.id},secondaryField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_secondaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.name},badgeField:{fieldName:this.knx.localize("telegram_filter_source_sort_by_badge"),filterable:!1,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>e.count.toString()}}}get _destinationFilterConfig(){return{idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_primaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.id},secondaryField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_secondaryText"),filterable:!0,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"asc",mapper:e=>e.name},badgeField:{fieldName:this.knx.localize("telegram_filter_destination_sort_by_badge"),filterable:!1,sortable:!0,sortAscendingText:this.knx.localize("telegram_filter_sort_ascending"),sortDescendingText:this.knx.localize("telegram_filter_sort_descending"),sortDefaultDirection:"desc",mapper:e=>e.count.toString()}}}get _directionFilterConfig(){return{idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{filterable:!1,sortable:!1,mapper:e=>e.id},secondaryField:{filterable:!1,sortable:!1,mapper:e=>e.name},badgeField:{filterable:!1,sortable:!1,mapper:e=>e.count.toString()}}}get _telegramTypeFilterConfig(){return{idField:{filterable:!1,sortable:!1,mapper:e=>e.id},primaryField:{filterable:!1,sortable:!1,mapper:e=>e.id},secondaryField:{filterable:!1,sortable:!1,mapper:e=>e.name},badgeField:{filterable:!1,sortable:!1,mapper:e=>e.count.toString()}}}_handleSortingChanged(e){this._sortColumn=e.detail.column}_handleRowClick(e){this._selectedTelegramId=e.detail.id}_handleDialogClosed(){this._selectedTelegramId=null}async _handlePauseToggle(){this._isPaused=!this._isPaused}async _handleReload(){await this._loadRecentTelegrams()}async _retryConnection(){this._connectionError=null,await this.firstUpdated()}_handleClearFilters(){this._filters={},this._updateUrlFromFilters()}_handleClearRows(){this._telegrams=[],this._resetDistinctValues(),this._isReloadEnabled=!0}_calculateTelegramStorageBuffer(e){const t=Math.ceil(.1*e),i=100*Math.ceil(t/100);return Math.max(i,k.MIN_TELEGRAM_STORAGE_BUFFER)}_enforceRingBufferLimit(e){return e.length<=this._telegramStorageLimit?e:e.slice(-this._telegramStorageLimit)}_mergeTelegrams(e,t){const i=new Set(e.map((e=>(e.cachedRow||(e.cachedRow=new _.g(e)),e.cachedRow.id)))),o=t.filter((e=>(e.cachedRow||(e.cachedRow=new _.g(e)),!i.has(e.cachedRow.id)))),r=[...e,...o];return r.sort(((e,t)=>new Date(e.timestamp).getTime()-new Date(t.timestamp).getTime())),this._enforceRingBufferLimit(r)}async _loadRecentTelegrams(){try{const e=await(0,g.Qm)(this.hass);this._isProjectLoaded=e.project_loaded;const t=e.recent_telegrams.length,i=this._calculateTelegramStorageBuffer(t);return this._telegramStorageLimit=t+i,this._telegrams=this._mergeTelegrams(this._telegrams,e.recent_telegrams),null!==this._connectionError&&(this._connectionError=null),this._initializeDistinctValues(this._telegrams,this._filters),this._isReloadEnabled=!1,!0}catch(e){return w.error("getGroupMonitorInfo failed",e),this._connectionError=e instanceof Error?e.message:String(e),!1}}_handleIncomingTelegram(e){if(this._isPaused)this._isReloadEnabled||(this._isReloadEnabled=!0);else{const t=[...this._telegrams,e];this._telegrams=this._enforceRingBufferLimit(t),this._updateDistinctValues(e)}}_unsubscribe(){this._subscribed&&(this._subscribed(),this._subscribed=void 0)}_navigateTelegram(e){if(!this._selectedTelegramId)return;const t=this.filteredRows.findIndex((e=>e.id===this._selectedTelegramId))+e;t>=0&&t<this.filteredRows.length&&(this._selectedTelegramId=this.filteredRows[t].id)}_selectNextTelegram(){this._navigateTelegram(1)}_selectPreviousTelegram(){this._navigateTelegram(-1)}_updateUrlFromFilters(){if(!this.route)return void w.warn("Route not available, cannot update URL");const e=new URLSearchParams;Object.entries(this._filters).forEach((([t,i])=>{Array.isArray(i)&&i.length>0&&e.set(t,i.join(","))}));const t=e.toString()?`${this.route.prefix}${this.route.path}?${e.toString()}`:`${this.route.prefix}${this.route.path}`;(0,d.c)(decodeURIComponent(t),{replace:!0})}_setFiltersFromUrl(){const e=new URLSearchParams(c.mainWindow.location.search),t=e.get("source"),i=e.get("destination"),o=e.get("direction"),r=e.get("telegramtype");(t||i||o||r)&&(this._filters={source:t?t.split(","):[],destination:i?i.split(","):[],direction:o?o.split(","):[],telegramtype:r?r.split(","):[]})}_shouldDisplayTelegram(e){return Object.entries(this._filters).every((([t,i])=>{if(!i?.length)return!0;const o={source:e.source,destination:e.destination,direction:e.direction,telegramtype:e.telegramtype};return i.includes(o[t]||"")}))}_toggleFilterValue(e,t){const i=this._filters[e]??[];i.includes(t)?this._filters={...this._filters,[e]:i.filter((e=>e!==t))}:this._filters={...this._filters,[e]:[...i,t]},this._updateUrlFromFilters()}_setFilterFieldValue(e,t){const i=this._filters[e]||[];this._filters={...this._filters,[e]:t},this._updateUrlFromFilters();const o=i.filter((e=>!t.includes(e)));o.length>0&&this._cleanupDistinctValuesForDeselectedItems(e,o)}_updateExpandedFilter(e,t){this._expandedFilter=t?e:this._expandedFilter===e?null:this._expandedFilter}_calculateRelativeTimeOffsets(e){if(e.length){e[0].offset=new Date(-1);for(let t=1;t<e.length;t++)e[t].offset=new Date(e[t].timestamp.getTime()-e[t-1].timestamp.getTime())}}_createEmptyDistinctValues(){return{source:{},destination:{},direction:{},telegramtype:{}}}_resetDistinctValues(){this._initializeDistinctValues([],this._filters)}_initializeDistinctValues(e,t){const i=this._createEmptyDistinctValues();t&&Object.entries(t).forEach((([e,t])=>{if(Array.isArray(t)&&t.length>0){const o=e;t.forEach((e=>{if(i[o]){const t=this._distinctValues[o]?.[e];i[o][e]={id:e,name:t?.name||"",count:0}}}))}}));for(const o of e)this._updateDistinctValueEntryLocal(i,"source",o.source,o.source_name||""),this._updateDistinctValueEntryLocal(i,"destination",o.destination,o.destination_name||""),this._updateDistinctValueEntryLocal(i,"direction",o.direction,""),this._updateDistinctValueEntryLocal(i,"telegramtype",o.telegramtype,"");this._distinctValues=i}_updateDistinctValueEntryLocal(e,t,i,o){i&&(e[t][i]?(e[t][i].count++,""===e[t][i].name&&(e[t][i].name=o)):e[t][i]={id:i,name:o,count:1})}_updateDistinctValues(e){const t={source:{...this._distinctValues.source},destination:{...this._distinctValues.destination},direction:{...this._distinctValues.direction},telegramtype:{...this._distinctValues.telegramtype}};this._updateDistinctValueEntryLocal(t,"source",e.source,e.source_name||""),this._updateDistinctValueEntryLocal(t,"destination",e.destination,e.destination_name||""),this._updateDistinctValueEntryLocal(t,"direction",e.direction,""),this._updateDistinctValueEntryLocal(t,"telegramtype",e.telegramtype,""),this._distinctValues=t}_cleanupDistinctValuesForDeselectedItems(e,t){const i=e,o=this._distinctValues[i];let r=!1;const a={...o};t.forEach((e=>{0===o[e]?.count&&(delete a[e],r=!0)})),r&&(this._distinctValues={...this._distinctValues,[i]:a})}_renderTelegramInfoDialog(e){const t=this.filteredRows.findIndex((t=>t.id===e)),i=this.filteredRows[t];return a.dy`
      <knx-telegram-info-dialog
        .hass=${this.hass}
        .knx=${this.knx}
        .telegram=${i}
        .disableNext=${t+1>=this.filteredRows.length}
        .disablePrevious=${t<=0}
        @next-telegram=${this._selectNextTelegram}
        @previous-telegram=${this._selectPreviousTelegram}
        @dialog-closed=${this._handleDialogClosed}
      >
      </knx-telegram-info-dialog>
    `}render(){const e=Object.values(this._filters).filter((e=>Array.isArray(e)&&e.length)).length;return a.dy`
      <hass-tabs-subpage-data-table
        .hass=${this.hass}
        .narrow=${this.narrow}
        .route=${this.route}
        .tabs=${this.tabs}
        .columns=${this._columns(this.narrow,this._isProjectLoaded,this.hass.language)}
        .noDataText=${this.knx.localize("group_monitor_waiting_message")}
        .data=${this.filteredRows}
        .hasFab=${!1}
        .searchLabel=${this.searchLabel}
        .localizeFunc=${this.knx.localize}
        id="id"
        .clickable=${!0}
        @row-click=${this._handleRowClick}
        @sorting-changed=${this._handleSortingChanged}
        has-filters
        .filters=${e}
        @clear-filter=${this._handleClearFilters}
      >
        <!-- Top header -->
        ${this._connectionError?a.dy`
              <ha-alert
                slot="top-header"
                .alertType=${"error"}
                .title=${this.knx.localize("group_monitor_connection_error_title")}
              >
                ${this._connectionError}
                <mwc-button
                  slot="action"
                  @click=${this._retryConnection}
                  .label=${this.knx.localize("group_monitor_retry_connection")}
                ></mwc-button>
              </ha-alert>
            `:a.Ld}
        ${this._isPaused?a.dy`
              <ha-alert
                slot="top-header"
                .alertType=${"info"}
                .dismissable=${!1}
                .title=${this.knx.localize("group_monitor_paused_title")}
              >
                ${this.knx.localize("group_monitor_paused_message")}
                <mwc-button
                  slot="action"
                  @click=${this._handlePauseToggle}
                  .label=${this.knx.localize("group_monitor_resume")}
                ></mwc-button>
              </ha-alert>
            `:""}

        <!-- Toolbar actions -->
        <div slot="toolbar-icon" class="toolbar-actions">
          <ha-icon-button
            .label=${this._isPaused?this.knx.localize("group_monitor_resume"):this.knx.localize("group_monitor_pause")}
            .path=${this._isPaused?b:v}
            class=${this._isPaused?"active":""}
            @click=${this._handlePauseToggle}
            data-testid="pause-button"
            .title=${this._isPaused?this.knx.localize("group_monitor_resume"):this.knx.localize("group_monitor_pause")}
          >
          </ha-icon-button>
          <ha-icon-button
            .label=${this.knx.localize("group_monitor_clear")}
            .path=${f}
            @click=${this._handleClearRows}
            ?disabled=${0===this._telegrams.length}
            data-testid="clean-button"
            .title=${this.knx.localize("group_monitor_clear")}
          >
          </ha-icon-button>
          <ha-icon-button
            .label=${this.knx.localize("group_monitor_reload")}
            .path=${y}
            @click=${this._handleReload}
            ?disabled=${!this._isReloadEnabled}
            data-testid="reload-button"
            .title=${this.knx.localize("group_monitor_reload")}
          >
          </ha-icon-button>
        </div>

        <!-- Filter for Source Address -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${this.hass}
          .knx=${this.knx}
          .data=${this.sourceDistinctValuesArray}
          .config=${this._sourceFilterConfig}
          .selectedOptions=${this._filters.source}
          .expanded=${"source"===this._expandedFilter}
          .narrow=${this.narrow}
          .filterTitle=${this.knx.localize("group_monitor_source")}
          @selection-changed=${this._handleSourceFilterChange}
          @expanded-changed=${this._handleSourceFilterExpanded}
        ></knx-list-filter>

        <!-- Filter for Destination Address -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${this.hass}
          .knx=${this.knx}
          .data=${this.destinationDistinctValuesArray}
          .config=${this._destinationFilterConfig}
          .selectedOptions=${this._filters.destination}
          .expanded=${"destination"===this._expandedFilter}
          .narrow=${this.narrow}
          .filterTitle=${this.knx.localize("group_monitor_destination")}
          @selection-changed=${this._handleDestinationFilterChange}
          @expanded-changed=${this._handleDestinationFilterExpanded}
        ></knx-list-filter>

        <!-- Filter for Direction -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${this.hass}
          .knx=${this.knx}
          .data=${this.directionDistinctValuesArray}
          .config=${this._directionFilterConfig}
          .selectedOptions=${this._filters.direction}
          .pinSelectedItems=${!1}
          .expanded=${"direction"===this._expandedFilter}
          .narrow=${this.narrow}
          .filterTitle=${this.knx.localize("group_monitor_direction")}
          @selection-changed=${this._handleDirectionFilterChange}
          @expanded-changed=${this._handleDirectionFilterExpanded}
        ></knx-list-filter>

        <!-- Filter for Telegram Type -->
        <knx-list-filter
          slot="filter-pane"
          .hass=${this.hass}
          .knx=${this.knx}
          .data=${this.telegramTypeDistinctValuesArray}
          .config=${this._telegramTypeFilterConfig}
          .selectedOptions=${this._filters.telegramtype}
          .pinSelectedItems=${!1}
          .expanded=${"telegramtype"===this._expandedFilter}
          .narrow=${this.narrow}
          .filterTitle=${this.knx.localize("group_monitor_type")}
          @selection-changed=${this._handleTelegramTypeFilterChange}
          @expanded-changed=${this._handleTelegramTypeFilterExpanded}
        ></knx-list-filter>
      </hass-tabs-subpage-data-table>

      <!-- Telegram detail dialog -->
      ${null!==this._selectedTelegramId?this._renderTelegramInfoDialog(this._selectedTelegramId):a.Ld}
    `}constructor(...e){super(...e),this._telegrams=[],this._selectedTelegramId=null,this._filters={},this._expandedFilter="source",this._isReloadEnabled=!1,this._isPaused=!1,this._isProjectLoaded=!1,this._connectionError=null,this._telegramStorageLimit=k.MIN_TELEGRAM_STORAGE_BUFFER,this._distinctValues={source:{},destination:{},direction:{},telegramtype:{}},this._getFilteredRows=(0,n.Z)(((e,t,i)=>{const o=e.filter((e=>this._shouldDisplayTelegram(e))).map((e=>(e.cachedRow||(e.cachedRow=new _.g(e)),e.cachedRow)));return"timestampIso"===i&&this._calculateRelativeTimeOffsets(o),o})),this._onFilterSelectionChange=(e,t)=>{this._setFilterFieldValue(e,t)},this._onFilterExpansionChange=(e,t)=>{this._updateExpandedFilter(e,t)},this._handleSourceFilterChange=e=>{this._onFilterSelectionChange("source",e.detail.value)},this._handleSourceFilterExpanded=e=>{this._onFilterExpansionChange("source",e.detail.expanded)},this._handleDestinationFilterChange=e=>{this._onFilterSelectionChange("destination",e.detail.value)},this._handleDestinationFilterExpanded=e=>{this._onFilterExpansionChange("destination",e.detail.expanded)},this._handleDirectionFilterChange=e=>{this._onFilterSelectionChange("direction",e.detail.value)},this._handleDirectionFilterExpanded=e=>{this._onFilterExpansionChange("direction",e.detail.expanded)},this._handleTelegramTypeFilterChange=e=>{this._onFilterSelectionChange("telegramtype",e.detail.value)},this._handleTelegramTypeFilterExpanded=e=>{this._onFilterExpansionChange("telegramtype",e.detail.expanded)},this._handleSourceFilterToggle=e=>{this._toggleFilterValue("source",e.detail.value)},this._handleDestinationFilterToggle=e=>{this._toggleFilterValue("destination",e.detail.value)},this._handleTelegramTypeFilterToggle=e=>{this._toggleFilterValue("telegramtype",e.detail.value)},this._columns=(0,n.Z)(((e,t,i)=>({timestampIso:{showNarrow:!1,filterable:!0,sortable:!0,direction:"desc",title:this.knx.localize("group_monitor_time"),minWidth:"110px",maxWidth:"120px",template:e=>a.dy`
          <knx-table-cell>
            <div class="primary" slot="primary">${(0,u.Yh)(e.timestamp)}</div>
            ${e.offset.getTime()>=0&&"timestampIso"===this._sortColumn?a.dy`
                  <div class="secondary" slot="secondary">
                    <span style="margin-right: 2px;">+</span>
                    <span>${(0,u.xi)(e.offset)}</span>
                  </div>
                `:a.Ld}
          </knx-table-cell>
        `},sourceAddress:{showNarrow:!0,filterable:!0,sortable:!1,title:this.knx.localize("group_monitor_source"),flex:2,minWidth:"0",template:e=>a.dy`
          <knx-table-cell-filterable
            .knx=${this.knx}
            .filterValue=${e.sourceAddress}
            .filterDisplayText=${e.sourceAddress}
            .filterActive=${(this._filters.source||[]).includes(e.sourceAddress)}
            @toggle-filter=${this._handleSourceFilterToggle}
          >
            <div class="primary" slot="primary">${e.sourceAddress}</div>
            ${e.sourceText?a.dy`
                  <div class="secondary" slot="secondary" title=${e.sourceText||""}>
                    ${e.sourceText}
                  </div>
                `:a.Ld}
          </knx-table-cell-filterable>
        `},sourceAddressNumeric:{hidden:!0,filterable:!1,sortable:!0,title:this.knx.localize("group_monitor_source")},sourceText:{hidden:!0,filterable:!0,sortable:!0,title:this.knx.localize("group_monitor_source_name")},sourceName:{showNarrow:!0,hidden:!0,sortable:!1,groupable:!0,filterable:!1,title:this.knx.localize("group_monitor_source")},destinationAddress:{showNarrow:!0,sortable:!1,filterable:!0,title:this.knx.localize("group_monitor_destination"),flex:2,minWidth:"0",template:e=>a.dy`
          <knx-table-cell-filterable
            .knx=${this.knx}
            .filterValue=${e.destinationAddress}
            .filterDisplayText=${e.destinationAddress}
            .filterActive=${(this._filters.destination||[]).includes(e.destinationAddress)}
            @toggle-filter=${this._handleDestinationFilterToggle}
          >
            <div class="primary" slot="primary">${e.destinationAddress}</div>
            ${e.destinationText?a.dy`
                  <div class="secondary" slot="secondary" title=${e.destinationText||""}>
                    ${e.destinationText}
                  </div>
                `:a.Ld}
          </knx-table-cell-filterable>
        `},destinationAddressNumeric:{hidden:!0,filterable:!1,sortable:!0,title:this.knx.localize("group_monitor_destination")},destinationText:{showNarrow:!0,hidden:!0,sortable:!0,filterable:!0,title:this.knx.localize("group_monitor_destination_name")},destinationName:{showNarrow:!0,hidden:!0,sortable:!1,groupable:!0,filterable:!1,title:this.knx.localize("group_monitor_destination")},type:{showNarrow:!1,title:this.knx.localize("group_monitor_type"),filterable:!0,groupable:!0,minWidth:"155px",maxWidth:"155px",template:e=>a.dy`
          <knx-table-cell-filterable
            .knx=${this.knx}
            .filterValue=${e.type}
            .filterDisplayText=${e.type}
            .filterActive=${(this._filters.telegramtype||[]).includes(e.type)}
            @toggle-filter=${this._handleTelegramTypeFilterToggle}
          >
            <div class="primary" slot="primary" title=${e.type}>${e.type}</div>
            <div
              class="secondary"
              slot="secondary"
              style="color: ${"Outgoing"===e.direction?"var(--knx-blue)":"var(--knx-green)"}"
            >
              ${e.direction}
            </div>
          </knx-table-cell-filterable>
        `},direction:{hidden:!0,title:this.knx.localize("group_monitor_direction"),filterable:!0,groupable:!0},payload:{showNarrow:!1,hidden:e&&t,title:this.knx.localize("group_monitor_payload"),filterable:!0,type:"numeric",minWidth:"105px",maxWidth:"105px",template:e=>e.payload?a.dy`
            <code
              style="
                display: inline-block;
                box-sizing: border-box;
                max-width: 100%;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.9em;
                background: var(--secondary-background-color);
                padding: 2px 4px;
                border-radius: 4px;
              "
              title=${e.payload}
            >
              ${e.payload}
            </code>
          `:a.Ld},value:{showNarrow:!0,hidden:!t,title:this.knx.localize("group_monitor_value"),filterable:!0,flex:1,minWidth:"0",template:e=>{const t=e.value;return t?a.dy`
            <knx-table-cell>
              <span
                class="primary"
                slot="primary"
                style="font-weight: 500; color: var(--primary-color);"
                title=${t}
              >
                ${t}
              </span>
            </knx-table-cell>
          `:""}}})))}}k.MIN_TELEGRAM_STORAGE_BUFFER=1e3,(0,r.__decorate)([(0,p.Cb)({type:Object})],k.prototype,"hass",void 0),(0,r.__decorate)([(0,p.Cb)({attribute:!1})],k.prototype,"knx",void 0),(0,r.__decorate)([(0,p.Cb)({type:Boolean,reflect:!0})],k.prototype,"narrow",void 0),(0,r.__decorate)([(0,p.Cb)({type:Object})],k.prototype,"route",void 0),(0,r.__decorate)([(0,p.Cb)({type:Array,reflect:!1})],k.prototype,"tabs",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_subscribed",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_telegrams",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_selectedTelegramId",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_filters",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_sortColumn",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_expandedFilter",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_isReloadEnabled",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_isPaused",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_isProjectLoaded",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_connectionError",void 0),(0,r.__decorate)([(0,p.SB)()],k.prototype,"_distinctValues",void 0),k=(0,r.__decorate)([(0,p.Mo)("knx-group-monitor")],k),o()}catch(f){o(f)}}))},78722:function(e,t,i){i.d(t,{D:()=>n});var o=i(87191),r=i(70323),a=i(1097);function n(e,t){const i=()=>(0,r.L)(t?.in,NaN),n=t?.additionalDigits??2,m=function(e){const t={},i=e.split(s.dateTimeDelimiter);let o;if(i.length>2)return t;/:/.test(i[0])?o=i[0]:(t.date=i[0],o=i[1],s.timeZoneDelimiter.test(t.date)&&(t.date=e.split(s.timeZoneDelimiter)[0],o=e.substr(t.date.length,e.length)));if(o){const e=s.timezone.exec(o);e?(t.time=o.replace(e[1],""),t.timezone=e[1]):t.time=o}return t}(e);let _;if(m.date){const e=function(e,t){const i=new RegExp("^(?:(\\d{4}|[+-]\\d{"+(4+t)+"})|(\\d{2}|[+-]\\d{"+(2+t)+"})$)"),o=e.match(i);if(!o)return{year:NaN,restDateString:""};const r=o[1]?parseInt(o[1]):null,a=o[2]?parseInt(o[2]):null;return{year:null===a?r:100*a,restDateString:e.slice((o[1]||o[2]).length)}}(m.date,n);_=function(e,t){if(null===t)return new Date(NaN);const i=e.match(l);if(!i)return new Date(NaN);const o=!!i[4],r=h(i[1]),a=h(i[2])-1,n=h(i[3]),s=h(i[4]),d=h(i[5])-1;if(o)return function(e,t,i){return t>=1&&t<=53&&i>=0&&i<=6}(0,s,d)?function(e,t,i){const o=new Date(0);o.setUTCFullYear(e,0,4);const r=o.getUTCDay()||7,a=7*(t-1)+i+1-r;return o.setUTCDate(o.getUTCDate()+a),o}(t,s,d):new Date(NaN);{const e=new Date(0);return function(e,t,i){return t>=0&&t<=11&&i>=1&&i<=(u[t]||(g(e)?29:28))}(t,a,n)&&function(e,t){return t>=1&&t<=(g(e)?366:365)}(t,r)?(e.setUTCFullYear(t,a,Math.max(r,n)),e):new Date(NaN)}}(e.restDateString,e.year)}if(!_||isNaN(+_))return i();const x=+_;let f,b=0;if(m.time&&(b=function(e){const t=e.match(d);if(!t)return NaN;const i=p(t[1]),r=p(t[2]),a=p(t[3]);if(!function(e,t,i){if(24===e)return 0===t&&0===i;return i>=0&&i<60&&t>=0&&t<60&&e>=0&&e<25}(i,r,a))return NaN;return i*o.vh+r*o.yJ+1e3*a}(m.time),isNaN(b)))return i();if(!m.timezone){const e=new Date(x+b),i=(0,a.Q)(0,t?.in);return i.setFullYear(e.getUTCFullYear(),e.getUTCMonth(),e.getUTCDate()),i.setHours(e.getUTCHours(),e.getUTCMinutes(),e.getUTCSeconds(),e.getUTCMilliseconds()),i}return f=function(e){if("Z"===e)return 0;const t=e.match(c);if(!t)return 0;const i="+"===t[1]?-1:1,r=parseInt(t[2]),a=t[3]&&parseInt(t[3])||0;if(!function(e,t){return t>=0&&t<=59}(0,a))return NaN;return i*(r*o.vh+a*o.yJ)}(m.timezone),isNaN(f)?i():(0,a.Q)(x+b+f,t?.in)}const s={dateTimeDelimiter:/[T ]/,timeZoneDelimiter:/[Z ]/i,timezone:/([Z+-].*)$/},l=/^-?(?:(\d{3})|(\d{2})(?:-?(\d{2}))?|W(\d{2})(?:-?(\d{1}))?|)$/,d=/^(\d{2}(?:[.,]\d*)?)(?::?(\d{2}(?:[.,]\d*)?))?(?::?(\d{2}(?:[.,]\d*)?))?$/,c=/^([+-])(\d{2})(?::?(\d{2}))?$/;function h(e){return e?parseInt(e):1}function p(e){return e&&parseFloat(e.replace(",","."))||0}const u=[31,null,31,30,31,30,31,31,30,31,30,31];function g(e){return e%400==0||e%4==0&&e%100!=0}},86253:function(e,t,i){i.d(t,{l:()=>n});var o=i(35340),r=i(83522);const a={},n=(0,r.XM)(class extends r.Xe{render(e,t){return t()}update(e,[t,i]){if(Array.isArray(t)){if(Array.isArray(this.ot)&&this.ot.length===t.length&&t.every(((e,t)=>e===this.ot[t])))return o.Jb}else if(this.ot===t)return o.Jb;return this.ot=Array.isArray(t)?Array.from(t):t,this.render(t,i)}constructor(){super(...arguments),this.ot=a}})}};
//# sourceMappingURL=6181.5faeb048d2d303c8.js.map