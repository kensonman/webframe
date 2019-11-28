/* File:    webframe/static/react.header.js
 * Date:    2019-1025 17:49
 * Author:  Kenson Man <kenson.idv.hk@gmail.com>
 */
class Menu extends React.Component{
   constructor(){
      super();
   }
   render(){
      console.log(this.props);
      return (
         <div id="pnl_header"><nav className="navbar navbar-expand-lg navbar-expand-md navbar-light bg-light">
            <span>{this.props.icon}, {this.props.text}</span>
            <a className="navbar-brand" href={this.props.url} title={this.props.dashboard}><Icon icon={this.props.icon} /> {this.props.text}</a>
         </nav></div>
/*
         <div id="pnl_header"><nav className="navbar navbar-expand-lg navbar-expand-md navbar-light bg-light">
            <Icon icon={this.props.icon} />
            <div className="collapse navbar-collapse" id="navbarCollapsibleContent">
               {this.props.children}
            </div>
         </nav></div>
*/
      );
   }
}
function Icon(props){
   if(!props.icon){ return null; }
   return (
      <i className={props.icon?'fas fa-'+props.icon:''}></i>
   );
};

function MenuItem(props){
   return (
      <li className="nav-item"><a className="nav-link" href={props.url} target={props.target?props.target:'_self'}>
         <Icon icon={props.icon} />&nbsp;
         {props.text.replace(/<!--.*-->/, '')}
      </a></li>
   );
};

function MenuSeparator(props){
   return <div className="dropdown-divider"></div>
};

class MenuDropdown extends React.Component{
   render(){
      return (
         <li className="nav-item dropdown">
            <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
               <Icon icon={this.props.icon} />&nbsp;
               {this.props.text.replace(/<!--.*-->/, '')} 
            </a>
            <ul className="dropdown-menu" aria-labelledby="navbarDropdown">
               {this.props.children}
           </ul>
         </li>
      );
   };
};

function MenuInput(props){
   return (
      <li className="nav-item">
         <form className="navbar-form navbar-left" role="search" action={props.action} style={props.style}>
            <div className="input-group">
                <input type="text" name={props.name} className="form-control" placeholder={props.text.replace(/<!--.*-->/, '')}/>
                <div className="input-group-append">
                   <span className="input-group-btn"><button className="btn btn-default" type="submit" title={props.text.replace(/<!--.*-->/, '')}><Icon icon={props.icon}/></button></span>
                </div>
            </div>
         </form>
      </li>
   );
};

