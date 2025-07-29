# -*- encoding: utf-8 -*-
# stub: rack-reverse-proxy-pact 1.0.2 ruby lib

Gem::Specification.new do |s|
  s.name = "rack-reverse-proxy-pact".freeze
  s.version = "1.0.2".freeze

  s.required_rubygems_version = Gem::Requirement.new(">= 0".freeze) if s.respond_to? :required_rubygems_version=
  s.require_paths = ["lib".freeze]
  s.authors = ["Jon Swope".freeze, "Ian Ehlert".freeze, "Roman Ernst".freeze, "Oleksii Fedorov".freeze]
  s.date = "2025-02-24"
  s.description = "A Rack based reverse proxy for basic needs.\nUseful for testing or in cases where webserver configuration is unavailable.\n".freeze
  s.email = ["jaswope@gmail.com".freeze, "ehlertij@gmail.com".freeze, "rernst@farbenmeer.net".freeze, "waterlink000@gmail.com".freeze]
  s.homepage = "https://github.com/waterlink/rack-reverse-proxy".freeze
  s.licenses = ["MIT".freeze]
  s.rubygems_version = "3.5.23".freeze
  s.summary = "A Simple Reverse Proxy for Rack".freeze

  s.installed_by_version = "3.5.16".freeze if s.respond_to? :installed_by_version

  s.specification_version = 4

  s.add_runtime_dependency(%q<rack>.freeze, [">= 3.0".freeze, "< 4.0".freeze])
  s.add_runtime_dependency(%q<rackup>.freeze, ["~> 2.0".freeze])
  s.add_runtime_dependency(%q<rack-proxy>.freeze, ["~> 0.6".freeze, ">= 0.6.1".freeze])
  s.add_development_dependency(%q<bundler>.freeze, [">= 1.7".freeze, "< 3.0".freeze])
  s.add_development_dependency(%q<rake>.freeze, [">= 10.3".freeze])
end
