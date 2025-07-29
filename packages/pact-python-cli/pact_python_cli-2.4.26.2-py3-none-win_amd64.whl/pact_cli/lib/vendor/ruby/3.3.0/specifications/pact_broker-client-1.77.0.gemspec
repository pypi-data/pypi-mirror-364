# -*- encoding: utf-8 -*-
# stub: pact_broker-client 1.77.0 ruby lib

Gem::Specification.new do |s|
  s.name = "pact_broker-client".freeze
  s.version = "1.77.0".freeze

  s.required_rubygems_version = Gem::Requirement.new(">= 0".freeze) if s.respond_to? :required_rubygems_version=
  s.require_paths = ["lib".freeze]
  s.authors = ["Beth Skurrie".freeze]
  s.date = "2024-10-24"
  s.description = "Client for the Pact Broker. Publish, retrieve and query pacts and verification results. Manage webhooks and environments.".freeze
  s.email = ["beth@bethesque.com".freeze]
  s.executables = ["pact-broker".freeze, "pactflow".freeze]
  s.files = ["bin/pact-broker".freeze, "bin/pactflow".freeze]
  s.homepage = "https://github.com/pact-foundation/pact_broker-client.git".freeze
  s.licenses = ["MIT".freeze]
  s.rubygems_version = "3.5.22".freeze
  s.summary = "See description".freeze

  s.installed_by_version = "3.5.16".freeze if s.respond_to? :installed_by_version

  s.specification_version = 4

  s.add_runtime_dependency(%q<httparty>.freeze, [">= 0.21.0".freeze, "< 1.0.0".freeze])
  s.add_runtime_dependency(%q<term-ansicolor>.freeze, ["~> 1.7".freeze])
  s.add_runtime_dependency(%q<table_print>.freeze, ["~> 1.5".freeze])
  s.add_runtime_dependency(%q<thor>.freeze, [">= 0.20".freeze, "< 2.0".freeze])
  s.add_runtime_dependency(%q<rake>.freeze, ["~> 13.0".freeze])
  s.add_runtime_dependency(%q<dig_rb>.freeze, ["~> 1.0".freeze])
  s.add_runtime_dependency(%q<base64>.freeze, ["~> 0.2".freeze])
  s.add_runtime_dependency(%q<ostruct>.freeze, [">= 0".freeze])
end
