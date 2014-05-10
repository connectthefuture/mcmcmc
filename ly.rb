#!/usr/bin/env ruby
require 'pry'
require 'json'

lyrics = JSON.parse(File.read('lyrics.json'))

def clean_string(string)
    string.gsub(/\(.*\)/, '').gsub(/\[.*\]/, '').gsub(/\*.*\*/, '').gsub(/\{.*\}/, '').gsub(/[,.!?\-'";=\(\)\{\}\*\[\]]/, '').downcase.strip
end
def clean_lyric(lyric)
    lyric.split(/\n/).map {|s| clean_string(s) }.reject(&:empty?).reject {|s| s.include? ':'}.join("\n")
end

lyrics.map! do |song|
    {
        'artist' => song['artist'],
        'song' => song['song'],
        'lyrics' => clean_lyric(song['lyrics'])
    }
end

File.open('scrubbed_lyrics.json', 'w') { |f| f.write lyrics.to_json}
