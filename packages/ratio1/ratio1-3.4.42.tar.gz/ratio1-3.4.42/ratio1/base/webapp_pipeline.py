import time
from .pipeline import Pipeline



class WebappPipeline(Pipeline):
  
  def __init__(
    self, 
    session, 
    log, 
    *, 
    node_addr, 
    name, 
    config={}, 
    plugins=[], 
    is_attached=False, 
    on_data=None,
    on_notification=None,
    existing_config=None, 
    extra_debug=False,
    **kwargs
  ) -> None:
    """
    This is a special type of pipeline that is used to deploy webapps.
    It will override the deploy method to return the ngrok URL as well as the on_data method to extract the ngrok URL.
    """
    self.app_url = None
    self.__extra_debug = extra_debug
    _on_data = [self.__check_payloads, on_data]    
    super().__init__(
      session, 
      log, 
      node_addr=node_addr, 
      name=name, 
      config=config, 
      plugins=plugins, 
      is_attached=is_attached, 
      on_data=_on_data,
      on_notification=on_notification,
      existing_config=existing_config, 
      
      **kwargs
    )
    return
  
  
  def __check_payloads(self, session, plugin_signature, plugin_instance, data):
    """
    Check if the payload if from ngrok and extract the ngrok URL.
    
    Parameters
    ----------
    
    
    session : Session
        The session object that received the payload.
            
    plugin_signature : str
        The signature of the plugin that sent the payload.
        
    plugin_instance : str
        The instance of the plugin that sent the payload.
        
    data : Payload
        The payload received from the edge node.     
        
         
    """
    if self.__extra_debug:
      self.P(f"Received payload from {plugin_signature} ({plugin_instance})")
    if "NGROK_URL" in data:
      self.app_url = data["NGROK_URL"]
    return
    
  def create_plugin_instance(
    self, 
    *, 
    signature, 
    instance_id, 
    config={},
    tunnel_engine='ngrok',
    tunnel_engine_enabled=True,
    ngrok_edge_label=None,
    cloudflare_token=None,
    **kwargs
  ):
    tunnel_kwargs = {
      'tunnel_engine': tunnel_engine,
      'tunnel_engine_enabled': tunnel_engine_enabled,
    }
    if not tunnel_engine_enabled:
      self.app_url = "TUNNEL_ENGINE_DISABLED"
    else:
      if tunnel_engine.lower() == 'cloudflare':
        if cloudflare_token is None:
          raise ValueError("Cloudflare token must be provided when using Cloudflare as tunnel engine.")
        self.P("Using Cloudflare as tunnel engine", color="green")
        self.app_url = "URL_DEFINED_IN_CLOUDFLARE_TOKEN"
        tunnel_kwargs['cloudflare_token'] = cloudflare_token
      else:
        self.P("Using ngrok as tunnel engine", color="green")
        if ngrok_edge_label is not None:
          self.app_url = "URL_DEFINED_IN_NGROK_EDGE_LABEL"
          tunnel_kwargs['ngrok_edge_label'] = ngrok_edge_label
        # endif ngrok_edge_label is not None
      # endif tunnel_engine ngrok or cloudflare
    # endif tunnel_engine_enabled
      
    return super().create_plugin_instance(
      signature=signature, 
      instance_id=instance_id, 
      config=config,
      **tunnel_kwargs,
      **kwargs
    )    
  
  def deploy(self, verbose=False, timeout=15, **kwargs):
    """
    Deploy the pipeline and return the URL of the webapp.
    
    Returns
    -------
    str
        The URL of the webapp.
    """
    res = super().deploy(verbose=verbose, timeout=timeout, **kwargs)
    # now we wait for the ngrok url to be available
    start = time.time()
    while self.app_url is None:
      elapsed = time.time() - start
      if elapsed > timeout:
        msg = "Timeout waiting for ngrok url"
        self.P(msg, color="red")
        raise Exception(msg)
    # return the ngrok url
    return self.app_url