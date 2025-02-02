FROM redmine:5.1.3
RUN sed -i -e "$ i RedmineApp::Application.routes.default_scope = \"/redmine\"" config/environment.rb
RUN echo "Redmine::Utils::relative_url_root = \"/redmine\"" >> config/environment.rb
RUN ln -sf ${PWD}/public ${PWD}/public/redmine
