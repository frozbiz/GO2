#
#  stats class for Gig-o-Matic 2 
#
# Aaron Oppenheimer
# 29 Jan 2014
#
from google.appengine.ext import ndb
from requestmodel import *
import webapp2_extras.appengine.auth.models

import webapp2
from debug import *

import assoc
import gig
import band

import logging
import json

def stats_key(member_name='stats_key'):
    """Constructs a Datastore key for a Stats entity with stats_name."""
    return ndb.Key('stats', stats_name)

class BandStats(ndb.Model):
    """ class to hold statistics """
    band = ndb.KeyProperty()
    date = ndb.DateProperty(auto_now_add=True)
    number_members = ndb.IntegerProperty()
    number_upcoming_gigs = ndb.IntegerProperty()
    number_gigs_created_today = ndb.IntegerProperty()
    
def get_band_stats(the_band_key):
    """ Return all the stats we have for a band """
    stats_query = BandStats.query( BandStats.band==the_band_key).order(BandStats.date)
    the_stats = stats_query.fetch()
    return the_stats
    
def make_band_stats(the_band_key):
    """ make a stats object for a band key and return it """
    the_stats = BandStats(band=the_band_key)

    all_member_keys = assoc.get_member_keys_of_band_key(the_band_key)
    the_stats.number_members = len(all_member_keys)
    logging.info("band {0} stats: {1} members".format(the_band_key.id(), the_stats.number_members))
    
    all_gigs = gig.get_gigs_for_band_keys(the_band_key, keys_only=True)
    the_stats.number_upcoming_gigs = len(all_gigs)
    logging.info("band {0} stats: {1} upcoming gigs".format(the_band_key.id(), the_stats.number_upcoming_gigs))
    
    today_gigs = gig.get_gigs_for_creation_date(the_band_key, the_stats.date)
    the_stats.number_gigs_created_today = len(today_gigs)
    
    the_stats.put()


#####
#
# Page Handlers
#
#####

class StatsPage(BaseHandler):
    """Page for showing stats"""

    @user_required
    def get(self):    
        self._make_page(the_user=self.user)
            
    def _make_page(self,the_user):

        the_bands = band.get_all_bands()

        stats=[]    
        for a_band in the_bands:
                
            a_stat = get_band_stats(a_band.key)
            
            the_count_data=[]
            for s in a_stat:
                the_count_data.append([s.date.year, s.date.month-1, s.date.day, s.number_members, s.number_upcoming_gigs])
            the_count_data_json=json.dumps(the_count_data)
            
            stats.append([a_band.name, a_band.key, the_count_data_json])
        
        template_args = {
            'the_stats' : stats
        }
        self.render_template('stats.html', template_args)


##########
#
# auto generate stats
#
##########
class AutoGenerateStats(BaseHandler):
    """ automatically generate statistics """
    def get(self):
        the_band_keys = band.get_all_bands(keys_only = True)
        for band_key in the_band_keys:
            make_band_stats(band_key)