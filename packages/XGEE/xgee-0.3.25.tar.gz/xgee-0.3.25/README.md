[![PyPI Downloads](https://static.pepy.tech/badge/xgee)](https://pepy.tech/projects/xgee)
# XGEE Framework launcher

This is the XGEE framework launcher for starting XGEE applications on your computer. 

# Purpose

The XGEE framework launcher is intended for hosting your XGEE application based on a YAML configuration file. It can host the single-page application through a *tornado* webserver as well as the EOQ model workspace.

# Preparing your App

To launch your XGEE application through the XGEE launcher you need to provide a YAML configuration file with the following parameters:

```
app:
  name: My XGEE application     # The application name
  port: 8080                    # The HTTP port of the application
eoq:    
  port: 8000                    # The EOQ WebSocket port of the application
  workspace: ./workspace        # The workspace folder of your application containing all model files
  actions: ./actions            # The actions folder of your application containing your EOQ actions
  meta: ./meta                  # The meta-model folder of your application containing your meta-models
  consolelog: true              # Logs the EOQ websocket log to the console. Alternatively, look at log/info.log
```

You need to place all of your single-page application files in the *app* subdirectory of your application directory. These files will be hosted by the XGEE framework. 

 **Note**: The XGEE framework hosts all XGEE core files in the http://localhost:port/xgee-core directory. You do not have to bundle these files with your application. Instead you need to adjust your relative include paths in your application to this directory.

You only need to supply the meta-models required for your application. All XGEE related meta-files are added to your EOQ server automatically, if hosted through the XGEE framework launcher.

 **Note**: The XGEE framework automatically loads the XGEE meta-models on your server. You should not include the XGEE meta-model files (e.g. *layout.ecore*) in your meta folder separately.

# Launching your XGEE application

You can launch your XGEE app by issuing the *xgee* command in your app directory from your terminal. If you want to launch multiple applications at once you can call the xgee command on a  directory *xgee ./apps*. The launcher will display an overview of your launched XGEE apps.

| App Name        | App Path    | Web Instance          |   EOQ Instance      |
| --------------- |:-----------:| :--------------------:|:--------------------:
| My application  | ./myapp     | http://localhost:8080 | ws://localhost:8000 |





