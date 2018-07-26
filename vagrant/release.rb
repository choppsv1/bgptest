#!/usr/bin/env ruby

require "http"
require 'optparse'

token = `secret-tool lookup passwords vagrant-token`.strip
version = File.read('VERSION').strip
user = ENV['USER']
box = "bgp-bionic"

api = HTTP.persistent("https://app.vagrantup.com").headers(
    "Content-Type" => "application/json",
    "Authorization" => "Bearer #{token}"
)

def http_fail(response, what)
    # Error, inspect the `errors` key for more information.
    puts "#{what} failed"
    p response.code, response.body
    exit(1)
end

options = {}
OptionParser.new do |parser|
    parser.on("-d", "--delete VERSION", "Delete the VERSION") do |version|
        puts "Deleting version #{version}"
        response = api.delete("/api/v1/box/#{user}/#{box}/version/#{version}")
        response.status.success? or http_fail response, "deleting #{version}"
        response.flush
        exit(0)
    end
end.parse!

# --------------
# Create version
# --------------
puts "creating version: #{version}"
response = api.post "/api/v1/box/#{user}/#{box}/versions",
                        json: { version: { version: "#{version}" } }
response.status.success? or http_fail response, "create version #{version}"
response.flush

# ---------------
# Create provider
# ---------------

#upload_path = "https://vagrantcloud.com/#{user}/boxes/#{box}/versions/#{version}/providers/virtualbox.box"

puts "creating provider: #{version}"
response = api.post "/api/v1/box/#{user}/#{box}/version/#{version}/providers",
                        json: { provider: { name: "virtualbox" } }
response.status.success? or http_fail response, "create provider for #{version}"
response.flush


# -----------------
# Upload a provider
# -----------------

puts "getting path for provider: #{version}"
response = api.get("/api/v1/box/#{user}/#{box}/version/#{version}/provider/virtualbox/upload")
# response.status.success? or http_fail response, "get upload path for provider for #{version}"
upload_path = response.parse['upload_path']

puts "uploading provider: #{version}"
HTTP.put upload_path, body: File.open("#{box}.box")

#system "curl --fail --header \"Authorization: Bearer #{token}\" #{upload_path} --request PUT --upload-file #{box}.box"
#$?.success? or raise "Failed upload: #{version}"
# # -------------------
# # Update the provider
# # -------------------

# puts "updated provider: #{version}"
# response = api.put("/api/v1/box/#{user}/#{box}/version/#{version}/provider/virtualbox", json: {
#                        provider: {
#                            name: "virtualbox",
#                            url: "#{upload_path}"
#                        }
#                    })
# response.status.success? or http_fail response, "Update provider for #{version}"
# response.flush

# -------
# release
# -------

puts "about to release: #{version}"
response = api.put("/api/v1/box/#{user}/#{box}/version/#{version}/release")
response.status.success? or http_fail response, "release #{version}"
response.flush

puts "released: #{version}"

#
# increment the version number
#

maj, min, patch =  version.match(/(\d+)\.(\d+)\.(\d+)/)[1..3]
patch = (patch.to_i + 1).to_s
version = "#{maj}.#{min}.#{patch}"

puts "setting up new version: #{version}"
File.write('VERSION', "#{version}\n")
